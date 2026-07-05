import pytest
import os
import sys

# Ensure the backend root is on the path so 'app' is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Point the app to a fresh in-memory database for every test run
os.environ["DATABASE_PATH"] = ":memory:"

from app import create_app


@pytest.fixture
def client():
    """Create a test Flask client backed by a fresh in-memory SQLite database."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
