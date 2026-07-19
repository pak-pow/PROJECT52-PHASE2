import sqlite3
import os
from app.config.settings import Config


def get_db():
    """Open and return a new SQLite connection with Row factory enabled."""
    conn = sqlite3.connect(Config.DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
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
