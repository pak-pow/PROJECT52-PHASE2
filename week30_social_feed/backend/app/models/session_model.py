import uuid
from app.db import get_db


def create_session(user_id):
    """Create a secure UUID session token and store it. Returns the token string."""
    token = uuid.uuid4().hex + uuid.uuid4().hex  # 64 hex chars
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id)
        )
        conn.commit()
        return token
    finally:
        conn.close()


def get_user_by_token(token):
    """Return user row for a valid session token, or None if invalid."""
    if not token or len(token) < 32:
        return None
    conn = get_db()
    try:
        return conn.execute(
            """SELECT u.*
               FROM users u
               JOIN sessions s ON s.user_id = u.id
               WHERE s.token = ?""",
            (token,),
        ).fetchone()
    finally:
        conn.close()


def delete_session(token):
    """Invalidate a session token (logout)."""
    conn = get_db()
    try:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
    finally:
        conn.close()


def delete_all_user_sessions(user_id):
    """Invalidate all sessions for a user (force logout from all devices)."""
    conn = get_db()
    try:
        conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()
