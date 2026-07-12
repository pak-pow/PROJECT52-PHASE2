import secrets
from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore
from app.db import get_db


# ── User CRUD ─────────────────────────────────────────────────────────────────

def create_user(username, password):
    """Create a new user and return their id. Raises ValueError if username taken."""
    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if existing:
            raise ValueError(f"Username '{username}' is already taken.")
        password_hash = generate_password_hash(password)
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def authenticate_user(username, password):
    """Verify credentials. Returns user row on success, None on failure."""
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            return user
        return None
    finally:
        conn.close()


def get_user_by_id(user_id):
    """Return a user row by id."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT id, username, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()


# ── Session CRUD ──────────────────────────────────────────────────────────────

def create_session(user_id):
    """Create a new session token for the given user. Returns the token string."""
    token = secrets.token_hex(32)
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO sessions (user_id, token) VALUES (?, ?)",
            (user_id, token)
        )
        conn.commit()
        return token
    finally:
        conn.close()


def get_user_by_token(token):
    """Look up a session token and return the associated user row, or None."""
    conn = get_db()
    try:
        row = conn.execute(
            """SELECT u.id, u.username, u.created_at
               FROM sessions s
               JOIN users u ON u.id = s.user_id
               WHERE s.token = ?""",
            (token,)
        ).fetchone()
        return row
    finally:
        conn.close()


def delete_session(token):
    """Delete a session by token (logout)."""
    conn = get_db()
    try:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
    finally:
        conn.close()
