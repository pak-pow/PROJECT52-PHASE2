from app.extensions.db import get_db

class Post:
    @staticmethod
    def get_all():
        db = get_db()
        return db.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()

    @staticmethod
    def create(title, content, author_id):
        db = get_db()
        cursor = db.execute(
            'INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)',
            (title, content, author_id)
        )
        db.commit()
        return cursor.lastrowid