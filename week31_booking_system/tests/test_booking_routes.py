import os
import sys

# Ensure backend/ is in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

import pytest
from app import create_app
from app.db import init_db
from app.config.settings import Config


@pytest.fixture
def app_instance(tmp_path):
    db_file = os.path.join(tmp_path, "test_booking.db")
    
    class TestConfig(Config):
        TESTING = True
        DEBUG = False
        DB_PATH = db_file

    # Copy schema to test db directory
    schema_src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", "data", "schema.sql")
    os.makedirs(os.path.join(tmp_path, "data"), exist_ok=True)
    with open(schema_src, "r", encoding="utf-8") as sf, open(os.path.join(tmp_path, "schema.sql"), "w", encoding="utf-8") as df:
        df.write(sf.read())

    app = create_app(TestConfig)
    with app.app_context():
        init_db()
    return app


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "week31_booking_system"


def test_user_registration_and_login(client):
    # Register
    reg_resp = client.post("/api/auth/register", json={
        "username": "testuser",
        "display_name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    })
    assert reg_resp.status_code == 201
    reg_data = reg_resp.get_json()
    assert "token" in reg_data
    assert reg_data["user"]["username"] == "testuser"

    # Login
    login_resp = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    assert login_resp.status_code == 200
    login_data = login_resp.get_json()
    assert "token" in login_data
