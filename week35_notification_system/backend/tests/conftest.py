import os
import pytest
from app.config.settings import Config
from app.db import init_db

TEST_DB_PATH = os.path.join(Config.BASE_DIR, "data", "test_notifications.db")

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    monkeypatch.setattr(Config, "DATABASE_PATH", TEST_DB_PATH)
    init_db()
    yield
