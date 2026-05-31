import sqlite3 
import os
from werkzeug.security import generate_password_hash #type: ignore

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'database.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql') 

def seed_database():
    pass

if __name__ == '__main__':
    seed_database()