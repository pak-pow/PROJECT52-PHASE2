import sqlite3
import os
from flask import g, current_app #type: ignore

def get_db():
    if 'db' not in g:
        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        db_path = os.path.join(base_dir, 'data', 'kanban.db')
        
        g.db = sqlite3.connect(
            db_path,
            detect_types = sqlite3.PARSE_DECLTYPES
        ) 
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON;')
        
    return g.db

def close_db(e = None):
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