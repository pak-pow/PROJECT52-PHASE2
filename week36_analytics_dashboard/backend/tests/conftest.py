import os
import pytest
from app.config.settings import Config
from app.db import init_db
from app import create_app

TEST_DB_PATH = os.path.join(Config.BASE_DIR, "data", "test_analytics.db")

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    monkeypatch.setattr(Config, "DATABASE_PATH", TEST_DB_PATH)
    init_db()
    yield

@pytest.fixture
def app_instance(monkeypatch):
    monkeypatch.setattr(Config, "DATABASE_PATH", TEST_DB_PATH)
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()
