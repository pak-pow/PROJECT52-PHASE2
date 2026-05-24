from app.extensions.db import get_db

class User:
    @staticmethod
    def get_by_username(username):
        db = get_db()
        return db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        return db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone() 