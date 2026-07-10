import pytest
import os
import sys

# Ensure the backend root is on the path so 'app' is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Use a shared in-memory SQLite database so all connections within a test share the same DB.
# Each test gets its own unique db name to prevent state leaking between tests.
import app.db as db_module

@pytest.fixture
def client(tmp_path):
    """Create a test Flask client backed by a temporary SQLite database."""
    db_file = tmp_path / "test_quiz.db"
    os.environ["DATABASE_PATH"] = str(db_file)
    db_module.DB_PATH = str(db_file)

    from app import create_app
    app = create_app()
    app.config["TESTING"] = True

    # Seed the test database
    from data.seed import seed, get_connection
    conn = get_connection()
    try:
        seed(conn)
    finally:
        conn.close()

    with app.test_client() as client:
        yield client

