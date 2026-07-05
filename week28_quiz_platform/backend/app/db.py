import sqlite3
import os

# Resolve paths relative to this file so the server can be run from any directory
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_DB = os.path.normpath(os.path.join(_BASE_DIR, "..", "data", "quiz.db"))

DB_PATH = os.environ.get("DATABASE_PATH", _DEFAULT_DB)
SCHEMA_PATH = os.path.normpath(os.path.join(_BASE_DIR, "..", "data", "schema.sql"))


def get_db():
    """Return a SQLite connection with row_factory set."""
    use_uri = DB_PATH.startswith("file:")
    conn = sqlite3.connect(DB_PATH, uri=use_uri, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Read and execute schema.sql to create tables and seed data."""
    schema_path = os.path.normpath(SCHEMA_PATH)
    with open(schema_path, "r") as f:
        sql = f.read()
    conn = get_db()
    conn.executescript(sql)
    conn.commit()
    conn.close()