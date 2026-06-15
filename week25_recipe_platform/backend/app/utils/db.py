import sqlite3
import os
from flask import g #type: ignore

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'data', 'database.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'data', 'schema.sql') 

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        
    return g.db

def init_db():
    db = get_db()
    
    with open(SCHEMA_PATH, 'r') as f:
        db.executescript(f.read())
        
    db.commit