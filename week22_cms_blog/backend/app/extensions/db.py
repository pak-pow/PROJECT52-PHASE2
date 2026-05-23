import sqlite3
import os
from flask import g, current_app #type: ignore

def get_db():
    
    if 'db' not in g:
        
        # getting the database file directory from the config file
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        
    return g.db

def close_db(e=None):
    
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    db_path = app.config['DATABASE']
    
    if not os.path.exists(db_path):
        print ("Initializing the Database...")         
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        with app.app_context():
            db = get_db()
            
            schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'schema.sql')
            with open(schema_path, 'r') as f:
                db.executescript(f.read())
                
            db.commit()
            
        print("Database built successfully")