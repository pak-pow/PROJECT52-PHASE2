"""Pytest configuration and shared fixtures for week30_social_feed."""
import os
import tempfile
import pytest
from app import create_app
from app.db import init_db


@pytest.fixture
def app():
    """Create a test Flask app with an isolated in-memory-like temp SQLite DB."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    test_config = {
        "TESTING": True,
        "DEBUG": False,
        "DB_PATH": db_path,
        "UPLOAD_DIR": tempfile.mkdtemp(),
        "AVATAR_DIR": tempfile.mkdtemp(),
        "POST_IMAGE_DIR": tempfile.mkdtemp(),
    }
    flask_app = create_app(test_config)
    yield flask_app
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Register a test user and return Bearer auth headers."""
    resp = client.post("/api/auth/register", json={
        "username": "testuser",
        "display_name": "Test User",
        "password": "securepass",
    })
    assert resp.status_code == 201
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
