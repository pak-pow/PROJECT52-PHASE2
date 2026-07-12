import os
import sys
import tempfile
import pytest

# Ensure the backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture()
def app(tmp_path):
    """Create a test app with an isolated temp database and upload directories."""
    db_path = str(tmp_path / "test.db")
    upload_dir = str(tmp_path / "uploads")
    thumb_dir = str(tmp_path / "thumbnails")

    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(thumb_dir, exist_ok=True)

    os.environ["DATABASE_PATH"] = db_path
    os.environ["UPLOAD_DIR"] = upload_dir
    os.environ["THUMBNAIL_DIR"] = thumb_dir

    from app import create_app
    application = create_app()
    application.config["TESTING"] = True

    yield application

    # Cleanup env vars
    for key in ("DATABASE_PATH", "UPLOAD_DIR", "THUMBNAIL_DIR"):
        os.environ.pop(key, None)


@pytest.fixture()
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture()
def auth_header(client):
    """Register a test user and return an Authorization header dict."""
    resp = client.post("/api/auth/register", json={
        "username": "testuser",
        "password": "testpass123",
    })
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
