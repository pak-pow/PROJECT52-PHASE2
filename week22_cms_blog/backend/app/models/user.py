from app.extensions.db import get_db
from werkzeug.security import check_password_hash #type: ignore

class User:
    @staticmethod
    def get_by_username(username):
        db = get_db()
        return db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        return db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    @staticmethod
    def verify_password(username, raw_password):
        user = User.get_by_username(username)
        if user and check_password_hash(user['password_hash'], raw_password):
            return user
        return None