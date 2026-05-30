from app.extensions.db import get_db

class Post:
    @staticmethod
    def get_all(status_filter=None):
        db = get_db()
        if status_filter:
            return db.execute('SELECT * FROM posts WHERE status = ? ORDER BY created_at DESC', (status_filter,)).fetchall()
        return db.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()

    @staticmethod
    def get_by_id(post_id):
        db = get_db()
        return db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()

    @staticmethod
    def create(title, content, author_id, status='draft'):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO posts (title, content, author_id, status) VALUES (?, ?, ?, ?)',
            (title, content, author_id, status)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def update(post_id, title, content, status):
        db = get_db()
        db.execute(
            'UPDATE posts SET title = ?, content = ?, status = ? WHERE id = ?',
            (title, content, status, post_id)
        )
        db.commit()

    @staticmethod
    def delete(post_id):
        db = get_db()
        db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        db.commit()