import sqlite3
from pathlib import Path
import subprocess


class GameDb():
    def __init__(self, file='game.db'):
        self.file=file

        if not Path(file).exists():
            with open('db_setup.sql', 'r') as sql_file:
                sql_stuff = sql_file.read()

            conn = sqlite3.connect(self.file)
            conn.row_factory = sqlite3.Row

            conn.executescript(sql_stuff)

            conn.commit()
            conn.close()

    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        self.conn.row_factory = sqlite3.Row
        return self

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

    def sql_fetchone(self, sql, data=()):
        return self.conn.execute(sql, data).fetchone()

    def sql_fetchall(self, sql, data=()):
        return self.conn.execute(sql, data).fetchall()

    def sql_commit(self, sql, data=()):
        self.conn.execute(sql, data)
        self.conn.commit()
