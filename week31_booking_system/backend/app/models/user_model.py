import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore
from app.db import get_db


def create_user(username, display_name, email, password, role="client"):
    """Create a new user. Returns user_id."""
    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?", (username, email)
        ).fetchone()
        if existing:
            raise ValueError("Username or email is already taken.")
        pwd_hash = generate_password_hash(password)
        cursor = conn.execute(
            "INSERT INTO users (username, display_name, email, role, password_hash) VALUES (?, ?, ?, ?, ?)",
            (username, display_name, email, role, pwd_hash)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        raise ValueError("Username or email is already taken.") from e
    finally:
        if not hasattr(conn, "commit"):
            conn.close()


def get_user_by_username(username):
    """Fetch user by username or None."""
    conn = get_db()
    return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def get_user_by_id(user_id):
    """Fetch user by id or None."""
    conn = get_db()
    return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def verify_password(username, password):
    """Verify credentials and return user row or None."""
    user = get_user_by_username(username)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None
