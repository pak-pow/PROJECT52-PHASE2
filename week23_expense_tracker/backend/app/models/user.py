import sqlite3
from app.utils.db import get_db

class User:
    @staticmethod
    def get_by_username(username):
        db = get_db()
        return db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        return db.execute('SELECT id, username, created_at FROM users WHERE id = ?', (user_id,)).fetchone()

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
            # Username already exists (UNIQUE constraint violation)
            return None