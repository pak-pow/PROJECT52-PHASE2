import sqlite3
import os
import tempfile
from flask import g

# Anchor everything to the backend/ directory
# db.py lives at: backend/app/utils/db.py
# So 2 levels up (.., ..) reaches backend/
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# Use a system temp directory for the SQLite database so that writes to it
# do not trigger VS Code Live Server file change detection and reload the browser page.
DB_PATH     = os.environ.get('DATABASE_PATH') or os.path.join(tempfile.gettempdir(), 'project52_url_shortener.db')
SCHEMA_PATH = os.path.join(BACKEND_DIR, 'data', 'schema.sql')



def get_db():
    """Open a new database connection if there isn't one in the current context."""
    if 'db' not in g:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
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
    _migrate_db(db)


def _migrate_db(db):
    """
    Apply incremental schema migrations on top of the existing database.

    SQLite does NOT support modifying column constraints after creation, so
    we use a table-rebuild approach (the official SQLite recommended method)
    when the live schema is stale.

    This prevents the common dev pitfall where schema.sql is updated but
    CREATE TABLE IF NOT EXISTS is a no-op on an already-existing table,
    leaving the app running against an outdated schema.
    """
    # Check if short_code still has a NOT NULL constraint (old schema)
    cols = db.execute("PRAGMA table_info(urls)").fetchall()
    col_map = {col['name']: col for col in cols}

    short_code_col = col_map.get('short_code')
    if short_code_col and short_code_col['notnull'] == 1:
        # Rebuild urls table with the correct (nullable short_code) schema
        db.executescript("""
            PRAGMA foreign_keys=OFF;

            CREATE TABLE IF NOT EXISTS urls_new (
                id           INTEGER   PRIMARY KEY AUTOINCREMENT,
                original_url TEXT      NOT NULL,
                short_code   VARCHAR(20) UNIQUE,
                clicks       INTEGER   DEFAULT 0,
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at   TIMESTAMP NULL
            );

            INSERT INTO urls_new (id, original_url, short_code, clicks, created_at, expires_at)
            SELECT id, original_url, short_code, clicks, created_at, expires_at FROM urls;

            DROP TABLE urls;
            ALTER TABLE urls_new RENAME TO urls;

            CREATE INDEX IF NOT EXISTS idx_short_code ON urls (short_code);

            PRAGMA foreign_keys=ON;
        """)
        db.commit()

