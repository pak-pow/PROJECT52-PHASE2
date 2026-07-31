import os
import sys
import datetime

# Ensure backend/ directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import create_app
from app.db import init_db, get_db
from app.config.settings import Config
from werkzeug.security import generate_password_hash  # type: ignore


@pytest.fixture
def app_instance(tmp_path):
    db_file = os.path.join(tmp_path, "test_booking.db")
    Config.DB_PATH = db_file

    # Copy schema to test db directory
    schema_src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "schema.sql")
    os.makedirs(os.path.join(tmp_path, "data"), exist_ok=True)
    with open(schema_src, "r", encoding="utf-8") as sf, open(os.path.join(tmp_path, "schema.sql"), "w", encoding="utf-8") as df:
        df.write(sf.read())

    app = create_app(Config)
    with app.app_context():
        init_db()
        _seed_test_data()
    return app


def _seed_test_data():
    """Seed test database with providers, services, and working hours."""
    conn = get_db()
    # Users
    pwd_hash = generate_password_hash("password123")
    client_id = conn.execute(
        "INSERT INTO users (username, display_name, email, role, password_hash) VALUES ('client1', 'Client One', 'client1@example.com', 'client', ?)",
        (pwd_hash,)
    ).lastrowid
    prov_user_id = conn.execute(
        "INSERT INTO users (username, display_name, email, role, password_hash) VALUES ('dr_test', 'Dr. Test', 'drtest@example.com', 'provider', ?)",
        (pwd_hash,)
    ).lastrowid

    # Provider
    provider_id = conn.execute(
        "INSERT INTO providers (user_id, title, bio) VALUES (?, 'Test Specialist', 'Bio test')",
        (prov_user_id,)
    ).lastrowid

    # Services
    service_id = conn.execute(
        "INSERT INTO services (title, description, duration_minutes, price, category) VALUES ('General Exam', 'Test Exam', 30, 50.0, 'Health')"
    ).lastrowid

    # Provider-Service Mapping
    conn.execute("INSERT INTO provider_services (provider_id, service_id) VALUES (?, ?)", (provider_id, service_id))

    # Working hours (Mon-Fri 09:00 - 17:00)
    for day in range(0, 5):
        conn.execute(
            "INSERT INTO provider_availability (provider_id, day_of_week, start_time, end_time) VALUES (?, ?, '09:00', '17:00')",
            (provider_id, day)
        )
    conn.commit()


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


def _get_auth_headers(client, username="client1", password="password123"):
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "week31_booking_system"


def test_user_registration_and_login(client):
    # Register
    reg_resp = client.post("/api/auth/register", json={
        "username": "newuser",
        "display_name": "New User",
        "email": "newuser@example.com",
        "password": "password123"
    })
    assert reg_resp.status_code == 201
    reg_data = reg_resp.get_json()
    assert "token" in reg_data
    assert reg_data["user"]["username"] == "newuser"

    # Login
    login_resp = client.post("/api/auth/login", json={
        "username": "newuser",
        "password": "password123"
    })
    assert login_resp.status_code == 200
    login_data = login_resp.get_json()
    assert "token" in login_data


def test_list_services_and_details(client):
    resp = client.get("/api/services")
    assert resp.status_code == 200
    services = resp.get_json()["services"]
    assert len(services) >= 1
    assert services[0]["title"] == "General Exam"

    # Get single service details
    sid = services[0]["id"]
    detail_resp = client.get(f"/api/services/{sid}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.get_json()
    assert detail_data["service"]["title"] == "General Exam"
    assert len(detail_data["providers"]) == 1


def test_check_provider_availability(client):
    # Get provider and service id
    services = client.get("/api/services").get_json()["services"]
    sid = services[0]["id"]
    providers = client.get("/api/providers").get_json()["providers"]
    pid = providers[0]["id"]

    # Choose a Monday in the future (e.g. 2026-08-03 is a Monday)
    target_date = "2026-08-03"
    avail_resp = client.get(f"/api/providers/{pid}/availability?service_id={sid}&date={target_date}")
    assert avail_resp.status_code == 200
    avail_data = avail_resp.get_json()
    assert len(avail_data["slots"]) > 0
    # All slots should initially be available
    assert all(s["available"] for s in avail_data["slots"])


def test_booking_creation_and_double_booking_conflict(client):
    headers = _get_auth_headers(client)
    services = client.get("/api/services").get_json()["services"]
    sid = services[0]["id"]
    providers = client.get("/api/providers").get_json()["providers"]
    pid = providers[0]["id"]

    target_date = "2026-08-03"
    start_time = "10:00"
    end_time = "10:30"

    # Create booking
    book_resp = client.post("/api/bookings", json={
        "provider_id": pid,
        "service_id": sid,
        "booking_date": target_date,
        "start_time": start_time,
        "end_time": end_time,
        "notes": "Test appointment"
    }, headers=headers)
    assert book_resp.status_code == 201
    booking_id = book_resp.get_json()["booking"]["id"]

    # Verify time slot is now unavailable in availability engine
    avail_resp = client.get(f"/api/providers/{pid}/availability?service_id={sid}&date={target_date}")
    slots = avail_resp.get_json()["slots"]
    slot_10 = next(s for s in slots if s["start_time"] == "10:00")
    assert slot_10["available"] is False

    # Attempt double-booking on overlapping slot -> should be rejected with 409 Conflict
    conflict_resp = client.post("/api/bookings", json={
        "provider_id": pid,
        "service_id": sid,
        "booking_date": target_date,
        "start_time": "10:15",
        "end_time": "10:45",
        "notes": "Conflicting attempt"
    }, headers=headers)
    assert conflict_resp.status_code == 409
    assert "no longer available" in conflict_resp.get_json()["error"]


def test_list_my_bookings_and_cancellation(client):
    headers = _get_auth_headers(client)
    services = client.get("/api/services").get_json()["services"]
    sid = services[0]["id"]
    providers = client.get("/api/providers").get_json()["providers"]
    pid = providers[0]["id"]

    target_date = "2026-08-04"
    book_resp = client.post("/api/bookings", json={
        "provider_id": pid,
        "service_id": sid,
        "booking_date": target_date,
        "start_time": "14:00",
        "end_time": "14:30"
    }, headers=headers)
    assert book_resp.status_code == 201
    bid = book_resp.get_json()["booking"]["id"]

    # List bookings
    list_resp = client.get("/api/bookings/my-bookings", headers=headers)
    assert list_resp.status_code == 200
    my_bookings = list_resp.get_json()["bookings"]
    assert any(b["id"] == bid for b in my_bookings)

    # Cancel booking
    cancel_resp = client.delete(f"/api/bookings/{bid}", headers=headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.get_json()["message"] == "Booking cancelled successfully."

    # Verify status changed to cancelled
    my_bookings_after = client.get("/api/bookings/my-bookings", headers=headers).get_json()["bookings"]
    cancelled_b = next(b for b in my_bookings_after if b["id"] == bid)
    assert cancelled_b["status"] == "cancelled"


def test_invalid_booking_date_format(client):
    headers = _get_auth_headers(client)
    resp = client.post("/api/bookings", json={
        "provider_id": 1,
        "service_id": 1,
        "booking_date": "invalid-date-string",
        "start_time": "10:00",
        "end_time": "10:30"
    }, headers=headers)
    assert resp.status_code == 400
    assert "Invalid 'booking_date' format" in resp.get_json()["error"]
