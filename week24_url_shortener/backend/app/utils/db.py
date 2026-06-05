import sqlite3
import os
from flask import g

# Anchor everything to the backend/ directory
# db.py lives at: backend/app/utils/db.py
# So 2 levels up (.., ..) reaches backend/
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH     = os.path.join(BACKEND_DIR, 'data', 'database.db')
SCHEMA_PATH = os.path.join(BACKEND_DIR, 'data', 'schema.sql')



def get_db():
    """Open a new database connection if there isn't one in the current context."""
    if 'db' not in g:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")   # Better concurrency
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Run schema.sql to create tables. Called once on first startup."""
    db = get_db()
    with open(SCHEMA_PATH, 'r') as f:
        db.executescript(f.read())
    db.commit()
