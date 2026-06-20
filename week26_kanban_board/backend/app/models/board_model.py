from app.utils.db import get_db

def get_all_boards():
    conn = get_db()
    cursor = conn.execute("SELECT * FROM boards ORDER BY created_at DESC")
    return [dict(row) for row in cursor.fetchall()]

def get_board_by_id(board_id):
    conn = get_db()
    cursor = conn.execute("SELECT * FROM boards WHERE id = ?", (board_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def create_board(title, description, accent_color):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO boards (title, description, accent_color) VALUES (?, ?, ?)",
        (title, description, accent_color)
    )
    conn.commit()
    return cursor.lastrowid

def update_board(board_id, title, description, accent_color):
    conn = get_db()
    conn.execute(
        "UPDATE boards SET title = ?, description = ?, accent_color = ? WHERE id = ?",
        (title, description, accent_color, board_id)
    )
    conn.commit()

def delete_board(board_id):
    conn = get_db()
    conn.execute("DELETE FROM boards WHERE id = ?", (board_id,))
    conn.commit()