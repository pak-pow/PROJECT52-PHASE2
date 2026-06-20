from app.utils.db import get_db

def get_cards_by_column(column_id):
    conn = get_db()
    cursor = conn.execute("SELECT * FROM cards WHERE column_id = ? ORDER BY position ASC", (column_id,))
    return [dict(row) for row in cursor.fetchall()]

def get_card_by_id(card_id):
    conn = get_db()
    cursor = conn.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def create_card(column_id, title, description):
    conn = get_db()
    # Auto-increment position to place at the bottom of the column
    cursor = conn.execute("SELECT MAX(position) FROM cards WHERE column_id = ?", (column_id,))
    max_pos = cursor.fetchone()[0]
    position = (max_pos + 1) if max_pos is not None else 0

    cursor = conn.execute(
        "INSERT INTO cards (column_id, title, description, position) VALUES (?, ?, ?, ?)",
        (column_id, title, description, position)
    )
    conn.commit()
    return cursor.lastrowid

def update_card(card_id, title, description):
    conn = get_db()
    conn.execute(
        "UPDATE cards SET title = ?, description = ? WHERE id = ?",
        (title, description, card_id)
    )
    conn.commit()

def delete_card(card_id):
    conn = get_db()
    conn.execute("DELETE FROM cards WHERE id = ?", (card_id,))
    conn.commit()

def move_card(card_id, new_column_id, new_position):
    conn = get_db()
    conn.execute(
        "UPDATE cards SET column_id = ?, position = ? WHERE id = ?",
        (new_column_id, new_position, card_id)
    )
    conn.commit()

def update_card_positions(updates):
    conn = get_db()
    cursor = conn.cursor()
    cursor.executemany("UPDATE cards SET position = ? WHERE id = ?", [(pos, cid) for cid, pos in updates])
    conn.commit()