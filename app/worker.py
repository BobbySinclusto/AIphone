from flask_socketio import SocketIO
import eventlet
import redis
import json
import os

from game_db import GameDb
from util import get_current_round_id, get_images_path, update_images, get_user_ids_for_game


eventlet.monkey_patch()


class Worker:
    def __init__(self, socketio: SocketIO) -> None:
        self.q = eventlet.Queue()
        self.r = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'))
        self.w = socketio.start_background_task(target=self.worker, socketio=socketio)

    def worker(self, socketio) -> None:
        print('starting worker...')
        while True:
            # this is necessary for some reason. ugh.
            self.q.get()
            _, data = self.r.blpop('flask_image_done')
            game_id, round_number, user_id, prompt, drawn_for, num_images = json.loads(data)

            # Update db
            with GameDb() as db:
                round_id = get_current_round_id(game_id, db)
                db.sql_commit('UPDATE Turns SET working = 1 WHERE user_id = ? AND round_id = ?', (user_id, round_id))

                # Rename images and add them to the db
                images_path = get_images_path(game_id=game_id, round_number=round_number, user_id=user_id)
                update_images(images_path=images_path, prompt=prompt, drawn_for=drawn_for, db=db)
            
            # Notify clients that images have been generated
            print('Done generating images, sending reload message via web socket')
            socketio.emit('reload', 'reload', to=user_id)
            self.q.task_done()

    def enqueue_prompt(self, game_id, round_number, user_id, prompt: str, drawn_for: str, num_images: int = 4):
        # don't ask
        self.q.put('work pls')
        self.r.lpush('image_to_generate', json.dumps([game_id, round_number, user_id, prompt, drawn_for, num_images]))
