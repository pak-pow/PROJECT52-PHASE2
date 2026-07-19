from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore
from app.db import get_db


def create_user(username, display_name, password):
    """Create a new user. Returns user_id. Raises ValueError if username taken."""
    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if existing:
            raise ValueError(f"Username '{username}' is already taken.")
        password_hash = generate_password_hash(password)
        cursor = conn.execute(
            "INSERT INTO users (username, display_name, password_hash) VALUES (?, ?, ?)",
            (username, display_name, password_hash),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_user_by_username(username):
    """Return user row by username or None."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id):
    """Return user row by id or None."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()


def verify_password(username, password):
    """Return user row if credentials are valid, else None."""
    user = get_user_by_username(username)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


def update_user_profile(user_id, display_name=None, bio=None, avatar_path=None):
    """Update mutable profile fields. Only updates provided (non-None) fields."""
    conn = get_db()
    try:
        if display_name is not None:
            conn.execute(
                "UPDATE users SET display_name = ? WHERE id = ?", (display_name, user_id)
            )
        if bio is not None:
            conn.execute(
                "UPDATE users SET bio = ? WHERE id = ?", (bio, user_id)
            )
        if avatar_path is not None:
            conn.execute(
                "UPDATE users SET avatar_path = ? WHERE id = ?", (avatar_path, user_id)
            )
        conn.commit()
    finally:
        conn.close()
