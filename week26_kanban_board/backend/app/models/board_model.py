from app.utils.db import get_db

def get_all_boards(user_id):
    conn = get_db()
    cursor = conn.execute("SELECT * FROM boards WHERE user_id = ? ORDER BY position ASC, created_at DESC", (user_id,))
    return [dict(row) for row in cursor.fetchall()]

def get_board_by_id(board_id):
    conn = get_db()
    cursor = conn.execute("SELECT * FROM boards WHERE id = ?", (board_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def create_board(user_id, title, description, accent_color):
    conn = get_db()
    
    # Calculate next position index
    cursor = conn.execute("SELECT COALESCE(MAX(position), -1) FROM boards WHERE user_id = ?", (user_id,))
    max_pos = cursor.fetchone()[0]
    next_pos = max_pos + 1
    
    cursor = conn.execute(
        "INSERT INTO boards (user_id, title, description, accent_color, position) VALUES (?, ?, ?, ?, ?)",
        (user_id, title, description, accent_color, next_pos)
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

def reorder_boards(updates):
    conn = get_db()
    for board_id, position in updates:
        conn.execute("UPDATE boards SET position = ? WHERE id = ?", (position, board_id))
    conn.commit()