import sqlite3
import os
from app.config.settings import Config

def get_db_connection():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = get_db_connection()
    if os.path.exists(Config.SCHEMA_PATH):
        with open(Config.SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
    conn.commit()
    conn.close()
