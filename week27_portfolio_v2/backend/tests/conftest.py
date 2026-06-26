import pytest #type:ignore
import sys
import os

# Ensure backend root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app #type:ignore
from app.db import get_db, init_db
from config import Config


class TestConfig(Config):
    """Override config for tests — use in-memory SQLite."""
    TESTING = True
    DATABASE = ":memory:"
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"


@pytest.fixture
def app():
    """Create application with in-memory DB for each test."""
    application = create_app(TestConfig)

    with application.app_context():
        init_db()

    yield application


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def admin_token(client):
    """Log in as admin and return a valid session token."""
    res = client.post(
        "/api/admin/login",
        json={"username": "admin", "password": "admin123"},
    )
    return res.get_json()["token"]


@pytest.fixture
def auth_headers(admin_token):
    """Return Authorization headers dict for admin requests."""
    return {"Authorization": f"Bearer {admin_token}"}
