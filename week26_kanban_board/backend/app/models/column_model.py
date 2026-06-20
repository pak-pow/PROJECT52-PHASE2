from app.utils.db import get_db

def get_columns_by_board(board_id):
    conn = get_db()
    cursor = conn.execute("SELECT * FROM columns WHERE board_id = ? ORDER BY position ASC", (board_id,))
    return [dict(row) for row in cursor.fetchall()]

def create_column(board_id, title):
    conn = get_db()
    cursor = conn.execute("SELECT MAX(position) FROM columns WHERE board_id = ?", (board_id,))
    max_pos = cursor.fetchone()[0]
    position = (max_pos + 1) if max_pos is not None else 0

    cursor = conn.execute(
        "INSERT INTO columns (board_id, title, position) VALUES (?, ?, ?)",
        (board_id, title, position)
    )
    conn.commit()
    return cursor.lastrowid

def update_column(column_id, title):
    conn = get_db()
    conn.execute("UPDATE columns SET title = ? WHERE id = ?", (title, column_id))
    conn.commit()

def delete_column(column_id):
    conn = get_db()
    conn.execute("DELETE FROM columns WHERE id = ?", (column_id,))
    conn.commit()

def update_column_positions(updates):
    conn = get_db()
    cursor = conn.cursor()
    cursor.executemany("UPDATE columns SET position = ? WHERE id = ?", [(pos, cid) for cid, pos in updates])
    conn.commit()