from app.db import get_db


def insert_file(user_id, original_name, stored_name, mime_type, file_size, category, has_thumbnail=False):
    """Insert a file metadata record and return its id."""
    conn = get_db()
    try:
        cursor = conn.execute(
            """INSERT INTO files (user_id, original_name, stored_name, mime_type, file_size, category, has_thumbnail)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, original_name, stored_name, mime_type, file_size, category, has_thumbnail)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_files(user_id, category=None):
    """Return all file metadata for a user, optionally filtered by category."""
    conn = get_db()
    try:
        if category and category != "all":
            rows = conn.execute(
                "SELECT * FROM files WHERE user_id = ? AND category = ? ORDER BY uploaded_at DESC",
                (user_id, category)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM files WHERE user_id = ? ORDER BY uploaded_at DESC",
                (user_id,)
            ).fetchall()
        return rows
    finally:
        conn.close()


def get_file_by_id(file_id, user_id):
    """Return a single file row owned by the given user, or None."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM files WHERE id = ? AND user_id = ?",
            (file_id, user_id)
        ).fetchone()
    finally:
        conn.close()


def delete_file_by_id(file_id, user_id):
    """Delete a file record. Returns the stored_name for disk cleanup, or None if not found."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT stored_name, has_thumbnail FROM files WHERE id = ? AND user_id = ?",
            (file_id, user_id)
        ).fetchone()
        if not row:
            return None
        conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
        conn.commit()
        return dict(row)
    finally:
        conn.close()
