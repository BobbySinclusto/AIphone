import os
from typing import Sequence
from pathlib import Path
from game_db import GameDb
from config import DATA_PATH

def get_user_ids_for_game(game_id, db: GameDb) -> Sequence[str]:
    return tuple(str(x[0]) for x in db.sql_fetchall('SELECT user_id FROM Players WHERE game_id = ?', (game_id,)))

def get_current_round_number(game_id, db: GameDb):
    return db.sql_fetchone('SELECT MAX(round_number) FROM Rounds WHERE game_id = ?', (game_id,))[0]

def get_current_round_id(game_id, db: GameDb):
    return db.sql_fetchone('SELECT id, MAX(round_number) FROM Rounds WHERE game_id = ? GROUP BY game_id', (game_id,))[0]

def get_images_path(game_id: str, round_number: str, user_id: str) -> Path:
    return Path(DATA_PATH).absolute().joinpath(f"{game_id}/{round_number}/{user_id}")

def update_images(images_path: Path, prompt: str, drawn_for: str, db: GameDb) -> Sequence[dict[str, Path]]:
    max_img_num = 0
    while images_path.joinpath(f'{max_img_num}.png').exists():
        max_img_num += 1

    imgs = []
    for img in sorted((images_path.joinpath(x) for x in images_path.glob('*')), key=os.path.getmtime):
        old_path = images_path.joinpath(img)
        new_path = old_path
        if not old_path.stem.isnumeric():
            new_path = images_path.joinpath(f"{max_img_num}.png")
            old_path.rename(new_path)
            max_img_num += 1
            # This is definitely a race condition lol, but it probably hopefully won't cause issues
            db.sql_commit('INSERT INTO Images (prompt, path, drawn_for) VALUES (?, ?, ?)', (prompt, str(new_path), drawn_for))
            image_id = db.sql_fetchone('SELECT id FROM Images WHERE path = ?', (str(new_path),))[0]
        else:
            image_id = db.sql_fetchone('SELECT id FROM Images WHERE path = ?', (str(new_path),))[0]

        imgs += [{'id': image_id, 'path': new_path}]
    
    return imgs
