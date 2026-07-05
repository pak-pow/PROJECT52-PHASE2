import sqlite3
import os

DB_PATH = os.environ.get("DATABASE_PATH", "data/quiz.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "schema.sql")


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