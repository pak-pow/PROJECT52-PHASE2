import pytest #type:ignore
import sys
import os
import importlib.util
import tempfile

# Add backend root to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Load app.py directly (avoids name collision with the app/ package)
_spec = importlib.util.spec_from_file_location("app_module", os.path.join(backend_dir, "app.py"))
_mod  = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
create_app = _mod.create_app

from app.db import init_db
from config import Config


class TestConfig(Config):
    """Override config for tests — use a temp file DB (not :memory:)
    so all SQLite connections within a test share the same data."""
    TESTING = True
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"


@pytest.fixture
def app():
    """Create application with a fresh temp-file DB for each test."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    class _TestConfig(TestConfig):
        DATABASE = db_path

    application = create_app(_TestConfig)

    # Push a permanent app context so init_db and all test requests share it
    ctx = application.app_context()
    ctx.push()
    init_db()

    yield application

    ctx.pop()
    os.unlink(db_path)


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
