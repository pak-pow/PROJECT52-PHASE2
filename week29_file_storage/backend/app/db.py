import sqlite3
import os

# Resolve paths relative to this file so the server can be run from any directory
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_DB = os.path.normpath(os.path.join(_BASE_DIR, "..", "data", "filestore.db"))

DB_PATH = os.environ.get("DATABASE_PATH", _DEFAULT_DB)
SCHEMA_PATH = os.path.normpath(os.path.join(_BASE_DIR, "..", "data", "schema.sql"))


def get_db():
    """Return a SQLite connection with row_factory set."""
    db_path = os.environ.get("DATABASE_PATH", DB_PATH)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Read and execute schema.sql to create tables."""
    conn = get_db()
    try:
        with open(SCHEMA_PATH, "r") as f:
            sql = f.read()
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()
