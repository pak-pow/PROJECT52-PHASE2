"""
conftest.py
Shared pytest fixtures for all test modules.

Provides:
  - app    : Flask test app wired to a fresh temp SQLite DB per test
  - client : Flask test client bound to the above app
  - board  : a pre-created board (id=1)
  - column : a pre-created column on board #1 (id=1)
  - card   : a pre-created card in column #1 (id=1)
"""
import os
import tempfile
import pytest

from app import create_app
from app.utils.db import init_db


# ---------------------------------------------------------------------------
# App + client fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """
    Creates a Flask app backed by a fresh temporary SQLite file.
    The file is deleted automatically after each test.
    """
    db_fd, db_path = tempfile.mkstemp(suffix='.db')

    test_app = create_app()
    test_app.config.update({
        'TESTING':  True,
        'DATABASE': db_path,
    })

    with test_app.app_context():
        init_db()   # apply schema.sql to the temp DB

    yield test_app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Flask test client — use this for route integration tests."""
    return app.test_client()


# ---------------------------------------------------------------------------
# Seed fixtures — build on each other so tests get realistic data
# ---------------------------------------------------------------------------

@pytest.fixture
def board(client):
    """Creates and returns a board via the API."""
    res = client.post('/api/boards', json={
        'title':        'Test Board',
        'description':  'A board for testing',
        'accent_color': '#6366f1',
    })
    assert res.status_code == 201
    return res.get_json()


@pytest.fixture
def column(client, board):
    """Creates and returns a column on the test board."""
    res = client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'To Do'})
    assert res.status_code == 201
    return res.get_json()


@pytest.fixture
def second_column(client, board):
    """Creates a second column — useful for card-move tests."""
    res = client.post(f'/api/boards/{board["id"]}/columns', json={'title': 'Done'})
    assert res.status_code == 201
    return res.get_json()


@pytest.fixture
def card(client, column):
    """Creates and returns a card in the test column."""
    res = client.post(f'/api/columns/{column["id"]}/cards', json={
        'title':       'Test Card',
        'description': 'A card for testing',
    })
    assert res.status_code == 201
    return res.get_json()
