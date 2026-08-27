import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.notification_model import NotificationModel
from app.config.settings import Config

@pytest.fixture
def app_instance():
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

def test_idempotency_key_creation(client):
    res = client.post("/api/notifications/send", json={
        "user_id": 301,
        "recipient": "idemp301@dev.io",
        "channel": "email",
        "content": "Idempotency test 1",
        "idempotency_key": "key_alpha_1"
    })
    assert res.status_code == 202
    assert res.get_json()["notification"]["idempotency_key"] == "key_alpha_1"

def test_idempotency_key_duplicate_returns_same_record(client):
    payload = {
        "user_id": 302,
        "recipient": "idemp302@dev.io",
        "channel": "email",
        "content": "Idempotency test 2",
        "idempotency_key": "key_beta_2"
    }
    r1 = client.post("/api/notifications/send", json=payload)
    n1_id = r1.get_json()["notification"]["id"]

    r2 = client.post("/api/notifications/send", json=payload)
    assert r2.status_code == 200
    assert r2.get_json()["notification"]["id"] == n1_id

def test_idempotency_key_different_keys_create_different_records(client):
    r1 = client.post("/api/notifications/send", json={
        "user_id": 303,
        "recipient": "idemp303@dev.io",
        "channel": "email",
        "content": "Content A",
        "idempotency_key": "key_gamma_1"
    })
    r2 = client.post("/api/notifications/send", json={
        "user_id": 303,
        "recipient": "idemp303@dev.io",
        "channel": "email",
        "content": "Content B",
        "idempotency_key": "key_gamma_2"
    })
    assert r1.get_json()["notification"]["id"] != r2.get_json()["notification"]["id"]

def test_idempotency_key_lookup_model_helper():
    NotificationModel.create_notification(
        user_id=304,
        recipient="helper@dev.io",
        channel="email",
        content="Model helper test",
        idempotency_key="key_delta_4"
    )
    found = NotificationModel.get_by_idempotency_key("key_delta_4")
    assert found is not None
    assert found["user_id"] == 304

def test_idempotency_key_lookup_nonexistent():
    assert NotificationModel.get_by_idempotency_key("non_existent_key_999") is None
    assert NotificationModel.get_by_idempotency_key(None) is None

def test_rate_limiting_counter_model_helper():
    u_id = 401
    initial_count = NotificationModel.count_recent_user_notifications(u_id, minutes=1)
    assert initial_count == 0

    NotificationModel.create_notification(u_id, "rate1@dev.io", "email", "Test 1")
    NotificationModel.create_notification(u_id, "rate2@dev.io", "email", "Test 2")

    new_count = NotificationModel.count_recent_user_notifications(u_id, minutes=1)
    assert new_count == 2

def test_rate_limiting_enforcement_at_max_limit(client):
    u_id = 505
    for i in range(Config.RATE_LIMIT_PER_MINUTE):
        r = client.post("/api/notifications/send", json={
            "user_id": u_id,
            "recipient": f"limit_{i}@dev.io",
            "channel": "email",
            "content": f"Msg {i}"
        })
        assert r.status_code == 202

    # Overflow request returns 429
    r_exceeded = client.post("/api/notifications/send", json={
        "user_id": u_id,
        "recipient": "exceed@dev.io",
        "channel": "email",
        "content": "Overflow"
    })
    assert r_exceeded.status_code == 429

def test_rate_limiting_per_user_isolation(client):
    u1 = 601
    u2 = 602

    # Fill u1 limit
    for i in range(Config.RATE_LIMIT_PER_MINUTE):
        client.post("/api/notifications/send", json={
            "user_id": u1,
            "recipient": "u1@dev.io",
            "channel": "email",
            "content": f"Msg {i}"
        })

    # u1 is limited
    r_u1 = client.post("/api/notifications/send", json={"user_id": u1, "recipient": "u1@dev.io", "channel": "email", "content": "Overflow"})
    assert r_u1.status_code == 429

    # u2 is NOT limited
    r_u2 = client.post("/api/notifications/send", json={"user_id": u2, "recipient": "u2@dev.io", "channel": "email", "content": "Fresh user request"})
    assert r_u2.status_code == 202

def test_idempotency_payload_variables_preserved(client):
    key = "key_json_var_test"
    payload = {
        "user_id": 701,
        "recipient": "vars@dev.io",
        "channel": "email",
        "content": "Rendered content",
        "variables": {"token": "xyz123", "amount": 99.99},
        "idempotency_key": key
    }
    r = client.post("/api/notifications/send", json=payload)
    assert r.status_code == 202
    variables = r.get_json()["notification"]["variables"]
    assert variables["token"] == "xyz123"

def test_serializer_handles_none_and_invalid_json():
    from app.services.serializers import serialize_notification
    raw_bad = {
        "id": 99,
        "variables_json": "INVALID_JSON_STRING",
        "user_id": 1,
        "recipient": "test@dev.io",
        "channel": "email",
        "content": "Bad JSON variables test"
    }
    serialized = serialize_notification(raw_bad)
    assert serialized["variables"] == {} # Safely defaults to empty dict
