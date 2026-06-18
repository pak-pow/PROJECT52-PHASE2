import sqlite3
import os
from flask import g  # type: ignore

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'data', 'database.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'data', 'schema.sql')


def get_db():
    """Opens a new database connection if there isn't one already for the current request context."""
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Closes the database connection at the end of a request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialises the database schema from schema.sql."""
    db = get_db()
    with open(SCHEMA_PATH, 'r') as f:
        db.executescript(f.read())
    db.commit()  # Fixed: was 'db.commit' (property reference, not a call)