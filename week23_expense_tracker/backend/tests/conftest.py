"""
Shared pytest fixtures used across all test modules.
"""
import pytest
import os
import tempfile
from app import create_app
from flask_jwt_extended import create_access_token  # type: ignore


@pytest.fixture
def app():
    """Creates a fresh temporary database and test application for each test."""
    db_fd, db_path = tempfile.mkstemp()

    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE": db_path,
        "JWT_SECRET_KEY": "test-secret-key-that-is-long-enough-32chars",
    })

    with app.app_context():
        from app.utils.db import get_db
        db = get_db()
        with open(os.path.join(app.root_path, '..', 'schema.sql'), 'r') as f:
            db.executescript(f.read())

        # Seed one default user for expense tests
        from werkzeug.security import generate_password_hash  # type: ignore
        db.execute(
            'INSERT INTO users (id, username, password_hash) VALUES (1, "testadmin", ?)',
            (generate_password_hash("Password123"),)
        )
        db.commit()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Provides a test HTTP client."""
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Generates a valid JWT token for User ID 1."""
    with app.app_context():
        token = create_access_token(identity="1")
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user_headers(app):
    """Generates a JWT token for a second user (ID 2) with no expenses."""
    with app.app_context():
        from app.utils.db import get_db
        from werkzeug.security import generate_password_hash  # type: ignore
        db = get_db()
        db.execute(
            'INSERT INTO users (id, username, password_hash) VALUES (2, "otheruser", ?)',
            (generate_password_hash("Password123"),)
        )
        db.commit()
        token = create_access_token(identity="2")
        return {"Authorization": f"Bearer {token}"}


def make_expense(client, auth_headers, amount=50.0, category="Food",
                 description="Test", date="2026-05-15"):
    """Helper to quickly create an expense and return the full response."""
    return client.post('/api/expenses/', json={
        "amount": amount,
        "category": category,
        "description": description,
        "date": date,
    }, headers=auth_headers)
