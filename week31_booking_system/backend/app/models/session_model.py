import uuid
from app.db import get_db


def create_session(user_id):
    """Create a new bearer session token for a user."""
    conn = get_db()
    token = uuid.uuid4().hex
    conn.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()
    return token


def get_user_by_token(token):
    """Return user dict associated with token or None."""
    if not token:
        return None
    conn = get_db()
    row = conn.execute(
        """SELECT u.id, u.username, u.display_name, u.email, u.role
           FROM sessions s
           JOIN users u ON u.id = s.user_id
           WHERE s.token = ?""",
        (token,)
    ).fetchone()
    return row


def delete_session(token):
    """Delete session token on logout."""
    conn = get_db()
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
