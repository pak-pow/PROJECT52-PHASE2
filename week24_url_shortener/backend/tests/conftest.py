import pytest
import os
from app import create_app
from app.utils.db import init_db

SCHEMA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'schema.sql')
)

@pytest.fixture
def app():
    """Create an isolated test Flask app with an in-memory SQLite database."""
    test_app = create_app()
    test_app.config.update({
        'TESTING': True,
    })

    with test_app.app_context():
        # Override DB to in-memory for tests
        import app.utils.db as db_module
        import sqlite3
        from flask import g

        def get_test_db():
            if 'db' not in g:
                g.db = sqlite3.connect(':memory:')
                g.db.row_factory = sqlite3.Row
                with open(SCHEMA_PATH, 'r') as f:
                    g.db.executescript(f.read())
            return g.db

        db_module.get_db = get_test_db
        yield test_app


@pytest.fixture
def client(app):
    return app.test_client()
