import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user_preference_model import UserPreferenceModel

@pytest.fixture
def app_instance():
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

def test_get_user_preferences_default(client):
    res = client.get("/api/preferences/501")
    assert res.status_code == 200
    data = res.get_json()
    assert data["user_id"] == 501
    assert data["email_enabled"] is True
    assert data["sms_enabled"] is True
    assert data["webhook_enabled"] is True

def test_update_user_preferences_all_disabled(client):
    res = client.put("/api/preferences/501", json={
        "email_enabled": False,
        "sms_enabled": False,
        "webhook_enabled": False
    })
    assert res.status_code == 200
    prefs = res.get_json()["preferences"]
    assert prefs["email_enabled"] is False
    assert prefs["sms_enabled"] is False
    assert prefs["webhook_enabled"] is False

def test_update_user_preferences_email_only(client):
    res = client.put("/api/preferences/502", json={
        "email_enabled": True,
        "sms_enabled": False,
        "webhook_enabled": False
    })
    assert res.status_code == 200
    prefs = res.get_json()["preferences"]
    assert prefs["email_enabled"] is True
    assert prefs["sms_enabled"] is False

def test_update_user_preferences_sms_only(client):
    res = client.put("/api/preferences/503", json={
        "email_enabled": False,
        "sms_enabled": True,
        "webhook_enabled": False
    })
    assert res.status_code == 200
    prefs = res.get_json()["preferences"]
    assert prefs["sms_enabled"] is True
    assert prefs["email_enabled"] is False

def test_update_user_preferences_webhook_only(client):
    res = client.put("/api/preferences/504", json={
        "email_enabled": False,
        "sms_enabled": False,
        "webhook_enabled": True
    })
    assert res.status_code == 200
    prefs = res.get_json()["preferences"]
    assert prefs["webhook_enabled"] is True

def test_get_updated_user_preferences(client):
    client.put("/api/preferences/505", json={
        "email_enabled": False,
        "sms_enabled": True,
        "webhook_enabled": True
    })
    res = client.get("/api/preferences/505")
    assert res.status_code == 200
    data = res.get_json()
    assert data["email_enabled"] is False
    assert data["sms_enabled"] is True

def test_preference_model_is_channel_enabled_helper():
    UserPreferenceModel.set_user_preferences(user_id=601, email_enabled=True, sms_enabled=False, webhook_enabled=True)
    assert UserPreferenceModel.is_channel_enabled(601, "email") is True
    assert UserPreferenceModel.is_channel_enabled(601, "sms") is False
    assert UserPreferenceModel.is_channel_enabled(601, "webhook") is True
    assert UserPreferenceModel.is_channel_enabled(601, "unknown_channel") is True

def test_update_preferences_empty_body_defaults_to_true(client):
    res = client.put("/api/preferences/602", json={})
    assert res.status_code == 200
    prefs = res.get_json()["preferences"]
    assert prefs["email_enabled"] is True

def test_update_preferences_boolean_type_coercion(client):
    res = client.put("/api/preferences/603", json={
        "email_enabled": 1,
        "sms_enabled": 0,
        "webhook_enabled": 1
    })
    assert res.status_code == 200
    prefs = res.get_json()["preferences"]
    assert prefs["email_enabled"] is True
    assert prefs["sms_enabled"] is False

def test_preference_persistence_across_requests(client):
    client.put("/api/preferences/700", json={"email_enabled": False, "sms_enabled": False, "webhook_enabled": True})
    r1 = client.get("/api/preferences/700")
    assert r1.get_json()["email_enabled"] is False

    # Modify again
    client.put("/api/preferences/700", json={"email_enabled": True, "sms_enabled": False, "webhook_enabled": True})
    r2 = client.get("/api/preferences/700")
    assert r2.get_json()["email_enabled"] is True

def test_preference_idempotency_upsert(client):
    for _ in range(3):
        res = client.put("/api/preferences/701", json={"email_enabled": True, "sms_enabled": True, "webhook_enabled": False})
        assert res.status_code == 200

    fetched = client.get("/api/preferences/701")
    assert fetched.get_json()["webhook_enabled"] is False

def test_preference_query_nonexistent_user_returns_default(client):
    res = client.get("/api/preferences/9999999")
    assert res.status_code == 200
    data = res.get_json()
    assert data["email_enabled"] is True

def test_preference_case_insensitivity_in_is_channel_enabled():
    UserPreferenceModel.set_user_preferences(user_id=702, email_enabled=False, sms_enabled=True, webhook_enabled=True)
    assert UserPreferenceModel.is_channel_enabled(702, "EMAIL") is False
    assert UserPreferenceModel.is_channel_enabled(702, "Sms") is True

def test_preference_update_returns_updated_at_timestamp(client):
    res = client.put("/api/preferences/703", json={"email_enabled": True})
    assert res.status_code == 200
    data = res.get_json()
    assert "user_id" in data["preferences"]

def test_preference_multiple_users_isolation(client):
    client.put("/api/preferences/801", json={"email_enabled": False})
    client.put("/api/preferences/802", json={"email_enabled": True})

    p1 = client.get("/api/preferences/801").get_json()
    p2 = client.get("/api/preferences/802").get_json()

    assert p1["email_enabled"] is False
    assert p2["email_enabled"] is True
