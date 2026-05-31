import sqlite3
from flask import g, current_app #type:ignore

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        
        # this returns a row as a dictionary not a tuple
        g.db.row_factory = sqlite3.Row 
    
    return g.db

def close_db():
    db = g.pop('db', None)
    if db is not None:
        db.close()