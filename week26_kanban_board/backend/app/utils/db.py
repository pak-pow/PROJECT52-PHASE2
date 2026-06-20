import sqlite3
import os
from flask import g, current_app  # type: ignore

_DEFAULT_DB_SUBPATH = os.path.join('data', 'kanban.db')


def _db_path() -> str:
    """
    Returns the DB path to use.
    Tests can override by setting app.config['DATABASE'] to a temp file path.
    """
    override = current_app.config.get('DATABASE')
    if override:
        return override
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    return os.path.join(base_dir, _DEFAULT_DB_SUBPATH)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(_db_path(), detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON;')
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    schema_path = os.path.join(base_dir, 'data', 'schema.sql')
    with open(schema_path, 'r') as f:
        db.executescript(f.read())
    db.commit()