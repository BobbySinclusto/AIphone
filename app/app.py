#!/usr/bin/env python3

from flask import Flask, send_file, render_template, send_from_directory, request, redirect
from flask_socketio import SocketIO, join_room, leave_room, send
from config import DATA_PATH, FLASK_SECRET_KEY
from game_db import GameDb
from worker import Worker
from util import update_images, get_images_path, get_current_round_id, get_current_round_number, get_user_ids_for_game

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
socketio = SocketIO(app)
worker = Worker(socketio)

# Join users to rooms based on their user_id so that messages are sent to the correct places
# This is probably the wrong way to use this but it works lol
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['user_id']
    print(f"{username} joined")
    join_room(room)
    print(f"{username} joined room {room}")

@socketio.on('leave')
def on_join(data):
    username = data['username']
    room = data['user_id']
    leave_room(room)
    print(f"{username} left")

@app.route("/")
def index():
    try:
        game_id = request.args['game_id']
        return render_template("login.html", game_id = game_id)
    except KeyError as ex:
        return render_template("login.html")

@app.route("/login", methods=['GET'])
def login():
    username = request.args['username']
    game_id = request.args['game_id']

    with GameDb() as db:
        # Create user account for user if they don't already have one
        if not db.sql_fetchone('SELECT id FROM Users WHERE username = ?', (username,)):
            db.sql_commit('INSERT INTO USERS (username) VALUES (?)', (username,))
        
        # Make sure the game exists
        if db.sql_fetchone('SELECT * FROM Games WHERE id = ?', (game_id,)):
            # Retrieve the user id
            user_id = db.sql_fetchone('SELECT id FROM Users WHERE username = ?', (username,))[0]
            # Add user id to game
            db.sql_commit('INSERT OR IGNORE INTO Players (user_id, game_id) VALUES (?, ?)', (user_id, game_id))
            # Notify existing users that a new player joined
            for id in get_user_ids_for_game(game_id, db):
                socketio.send(f"{username} joined", to=id)
            return redirect(f"/game?user_id={user_id}&game_id={game_id}")

@app.route("/create_game", methods=['GET'])
def create_game():
    num_turns = request.args['num_turns']
    with GameDb() as db:
        db.sql_commit('INSERT INTO Games (num_turns) VALUES (?)', (num_turns,))
        game_id = db.sql_fetchone('SELECT MAX(id) FROM Games')[0]
        db.sql_commit('INSERT INTO Rounds (round_number, game_id) VALUES (?, ?)', (0, game_id))
        return redirect(f"/?game_id={game_id}")

@app.route("/game", methods=['GET'])
def game():
    user_id = request.args['user_id']
    game_id = request.args['game_id']
    wait = request.args.get('wait', 0) == '1'

    ctx = {
        'user_id': user_id,
        'game_id': game_id,
        'wait': wait,
    }

    with GameDb() as db:
        round_id = get_current_round_id(game_id, db)
        round_number = get_current_round_number(game_id, db)
        ctx['username'] = db.sql_fetchone('SELECT username FROM Users WHERE id = ?', (user_id,))[0]
        ctx['round_number'] = round_number
        ctx['drawn_for'] = user_id
        user_ids = db.sql_fetchall('SELECT user_id, username FROM Players INNER JOIN Users ON Players.user_id = Users.id WHERE game_id = ?', (game_id,))

        # Get status for each player
        ctx['all_players_info'] = []
        for user in user_ids:
            current_user_id, current_user_name = user
            res = db.sql_fetchone('SELECT working, ready FROM Turns WHERE user_id = ? AND round_id = ?', (current_user_id, round_id))
            player_status = "writing prompt"
            if res:
                current_user_working, current_user_ready = res
                if current_user_working:
                    player_status = "waiting for image generation"
                elif current_user_ready:
                    player_status = "ready for next round"
                else:
                    player_status = "choosing image"
            ctx['all_players_info'] += [{'name': current_user_name, 'status': player_status}]
        
        # If round number is equal to number of rounds, display results
        num_rounds = db.sql_fetchone('SELECT num_turns FROM Games WHERE id = ?', (game_id,))[0]
        if round_number == num_rounds:
            player_rounds_list = []
            for user in (x[0] for x in user_ids):
                current_user_name = db.sql_fetchone('SELECT username FROM Users WHERE id = ?', (user,))[0]
                user_round_info_raw = db.sql_fetchall('''
                    SELECT Users.username, Images.prompt, Images.id FROM Images
                    INNER JOIN Turns ON Images.id = Turns.image_id
                    INNER JOIN Users ON Turns.user_id = Users.id
                    INNER JOIN Rounds ON Rounds.id = Turns.round_id
                    WHERE Images.drawn_for = ? AND Rounds.game_id = ?
                    ORDER BY Rounds.round_number
                ''', (user, game_id))
                user_round_info = [{'username': x[0], 'prompt': x[1], 'image_id': x[2]} for x in user_round_info_raw]
                player_rounds_list += [{'username': current_user_name, 'rounds': user_round_info}]
            ctx['player_rounds_list'] = player_rounds_list
            return render_template('results.html', **ctx)

        # If not round 0, display the next user's thingamabob
        if round_number != 0:
            prev_user = user_ids[-1]
            i = 0
            while str(user_ids[i][0]) != user_id:
                prev_user = user_ids[i]
                i += 1
            prev_user_id, prev_user_name = prev_user
            ctx['drawn_for'] = user_ids[(i - round_number) % len(user_ids)][0]
            ctx['prev_user_name'] = prev_user_name

            ctx['prev_user_image_id'] = db.sql_fetchone('SELECT image_id FROM Turns INNER JOIN Rounds ON Turns.round_id = Rounds.id WHERE round_number = ? AND user_id = ? AND game_id = ?', (round_number - 1, prev_user_id, game_id))[0]

        # Check if user is waiting on queue
        turn_info = db.sql_fetchone('SELECT prompt, ready, image_id FROM Turns WHERE round_id = ? and user_id = ?', (round_id, user_id))
        if turn_info:
            prompt, ready, image_id = turn_info
            if not ready:
                image_id = None
            ctx['prompt'] = prompt
            ctx['ready'] = ready
            ctx['chosen_image_id'] = image_id
        
            # Get images
            images_path = get_images_path(game_id=game_id, round_number=round_number, user_id=user_id)
            ctx['images'] = update_images(db=db, images_path=images_path, prompt=prompt, drawn_for=ctx['drawn_for'])
            ctx['generated_images'] = True

        return render_template('game.html', **ctx)

@app.route("/submit_prompt", methods=['POST'])
def submit_prompt():
    user_id = request.form['user_id']
    drawn_for = request.form['drawn_for']
    game_id = request.form['game_id']
    prompt = request.form['prompt']
    num_images = int(request.form['num_images'])
    if num_images > 4:
        num_images = 4

    with GameDb() as db:
        round_id = get_current_round_id(game_id, db)
        existing_turn = db.sql_fetchone('SELECT working FROM Turns WHERE user_id = ? AND round_id = ?', (user_id, round_id))
        if existing_turn and existing_turn[0]:
            return redirect(f"/game?user_id={user_id}&game_id={game_id}&wait=1")
        
        round_number = get_current_round_number(game_id, db)
        if not existing_turn:
            db.sql_commit('INSERT INTO Turns (round_id, user_id, prompt, working, ready) VALUES (?, ?, ?, 1, 0)', (round_id, user_id, prompt))
        else:
            db.sql_commit('UPDATE Turns SET working = 1, prompt = ? WHERE round_id = ? AND user_id = ?', (prompt, round_id, user_id))

        # Generate new images
        worker.enqueue_prompt(drawn_for=drawn_for, game_id=game_id, num_images=num_images, prompt=prompt, round_number=round_number, user_id=user_id)

        # Alert users that this user is generating images
        username = db.sql_fetchone('SELECT username FROM Users WHERE id = ?', (user_id,))[0]
        for id in get_user_ids_for_game(game_id, db):
            socketio.send(f"{username} is generating their images", to=id)

        return redirect(f"/game?user_id={user_id}&game_id={game_id}")

@app.route("/choose_image")
def choose_image():
    user_id = request.args['user_id']
    game_id = request.args['game_id']
    image_id = request.args['image_id']

    with GameDb() as db:
        round_id = get_current_round_id(game_id, db)
        round_number = get_current_round_number(game_id, db)
        prompt = db.sql_fetchone('SELECT prompt FROM Images WHERE id = ?', (image_id,))[0]
        db.sql_commit('UPDATE Turns SET prompt = ?, ready = 1, image_id = ? WHERE round_id = ? and user_id = ?', (prompt, image_id, round_id, user_id))

        # Alert users that this user is ready
        username = db.sql_fetchone('SELECT username FROM Users WHERE id = ?', (user_id,))[0]
        for id in get_user_ids_for_game(game_id, db):
            socketio.send(f"{username} is ready", to=id)

        # If all users are ready, update the round number
        if not db.sql_fetchall(
            '''
                SELECT Players.user_id
                FROM Players
                LEFT JOIN (
                    SELECT * FROM Rounds
                    INNER JOIN Turns ON Rounds.id = Turns.round_id
                    WHERE Rounds.round_number = ? AND Rounds.id = ?
                ) a ON a.user_id = Players.user_id
                WHERE Players.game_id = ? AND (ready = 0 OR ready IS NULL)
            ''', 
            (round_number, round_id, game_id),
        ):
            db.sql_commit('INSERT INTO Rounds (round_number, game_id) VALUES (?, ?)', (round_number + 1, game_id))
            # Reload all clients (move to next round)
            for id in get_user_ids_for_game(game_id, db):
                socketio.emit('reload', 'reload', to=id)


    return redirect(f"/game?user_id={user_id}&game_id={game_id}")

@app.route('/images')
def send_image():
    image_id = request.args['id']
    with GameDb() as db:
        return send_file(db.sql_fetchone('SELECT path FROM Images WHERE id = ?', (image_id,))[0])

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
