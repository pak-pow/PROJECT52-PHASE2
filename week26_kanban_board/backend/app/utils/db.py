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

def close_db():
    pass

def init_db():
    pass

