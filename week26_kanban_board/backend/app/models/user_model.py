import secrets
from app.utils.db import get_db

def create_user(username, password_hash):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )
    conn.commit()
    return cursor.lastrowid

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.execute("SELECT id, username, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

def get_user_by_username(username):
    conn = get_db()
    cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    return dict(row) if row else None

def create_session(user_id):
    token = secrets.token_hex(32)
    conn = get_db()
    conn.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()
    return token

def get_user_by_session_token(token):
    conn = get_db()
    cursor = conn.execute(
        "SELECT users.id, users.username, users.created_at FROM users "
        "JOIN sessions ON users.id = sessions.user_id WHERE sessions.token = ?",
        (token,)
    )
    row = cursor.fetchone()
    return dict(row) if row else None

def delete_session(token):
    conn = get_db()
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
