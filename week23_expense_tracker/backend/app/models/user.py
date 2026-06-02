import sqlite3
from app.utils.db import get_db

class User:
    @staticmethod
    def get_by_username(username):
        db = get_db()
        return db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

    @staticmethod
    def create(username, password_hash):
        """Inserts a new user into the database."""
        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
            db.commit()
            return cursor.lastrowid

        except sqlite3.IntegrityError:
            return None