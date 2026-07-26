import sqlite3
import os
from flask import g
from app.config.settings import Config


def get_db():
    """Connect to SQLite database or return current thread's connection."""
    try:
        if "db" not in g:
            g.db = sqlite3.connect(Config.DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON;")
            g.db.execute("PRAGMA journal_mode = WAL;")
        return g.db
    except RuntimeError:
        conn = sqlite3.connect(Config.DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn


def close_db(e=None):
    """Close SQLite connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Initialise SQLite database using schema.sql."""
    db_dir = os.path.dirname(Config.DB_PATH)
    os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(Config.DB_PATH)
    schema_path = os.path.join(db_dir, "schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
    conn.commit()
    conn.close()
