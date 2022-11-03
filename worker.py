import queue
import threading
import subprocess
from game_db import GameDb
from util import get_current_round_id, get_images_path, update_images
from config import DATA_PATH, STABLE_DIFFUSION_PATH
from pathlib import Path

def worker(q: queue.Queue) -> None:
    while True:
        game_id, round_number, user_id, prompt, num_images, drawn_for = q.get()

        print(f"Generating images for:\nGame:\t{game_id}\nRound:\t{round_number}\nUser:\t{user_id}")

        images_path = get_images_path(game_id=game_id, round_number=round_number, user_id=user_id)
        images_path.mkdir(parents=True, exist_ok=True)

        # Update db
        with GameDb() as db:
            round_id = get_current_round_id(game_id, db)
            db.sql_commit('UPDATE Turns SET working = 1 WHERE user_id = ? AND round_id = ?', (user_id, round_id))

        error = False
        try:
            subprocess.run(
                (
                    'docker',
                    'run',
                    '--rm',
                    '--gpus=all',
                    '-v',
                    'huggingface:/home/huggingface/.cache/huggingface',
                    '-v',
                    f'{images_path}:/home/huggingface/output',
                    'stable-diffusion-docker',
                    '--half',
                    '--skip',
                    '--n_iter',
                    str(num_images),
                    '--prompt',
                    prompt
                ),
                cwd=STABLE_DIFFUSION_PATH,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True
            )
        except subprocess.CalledProcessError as ex:
            import traceback
            traceback.print_exception(ex)
            print(ex.stdout.decode())
            error = True
        
        # Update db
        with GameDb() as db:
            if error:
                db.sql_commit('DELETE FROM Turns WHERE user_id = ? AND round_id = ?', (user_id, round_id))
            else:
                db.sql_commit('UPDATE Turns SET working = 0 WHERE user_id = ? AND round_id = ?', (user_id, round_id))

                # Rename images and add them to the db
                update_images(images_path=images_path, prompt=prompt, drawn_for=drawn_for, db=db)

        q.task_done()

q = queue.Queue()
w = threading.Thread(target=worker, args=(q,))
w.start()

def enqueue_prompt(game_id, round_number, user_id, prompt: str, drawn_for: str, num_images: int = 4):
    q.put((game_id, round_number, user_id, prompt, num_images, drawn_for))
