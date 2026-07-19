import sqlite3
import os
from app.config.settings import Config

try:
    from flask import current_app
    _has_flask = True
except ImportError:
    _has_flask = False


def _db_path():
    """Return the active DB path — prefers current Flask app config over class default."""
    if _has_flask:
        try:
            return current_app.config.get("DB_PATH", Config.DB_PATH)
        except RuntimeError:
            pass
    return Config.DB_PATH


def get_db():
    """Open and return a new SQLite connection with Row factory enabled."""
    conn = sqlite3.connect(_db_path(), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db():
    """Execute schema.sql to create all tables and indexes (idempotent)."""
    schema_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data", "schema.sql"
    )
    conn = get_db()
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()
