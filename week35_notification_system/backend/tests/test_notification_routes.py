import os
import sys
import time
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.template_model import TemplateModel
from app.models.user_preference_model import UserPreferenceModel
from app.config.settings import Config

@pytest.fixture
def app_instance():
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

def test_send_notification_missing_required_fields_400(client):
    res = client.post("/api/notifications/send", json={})
    assert res.status_code == 400
    assert "required" in res.get_json()["error"]

def test_send_notification_missing_recipient_400(client):
    res = client.post("/api/notifications/send", json={"user_id": 1, "channel": "email"})
    assert res.status_code == 400

def test_send_notification_missing_channel_400(client):
    res = client.post("/api/notifications/send", json={"user_id": 1, "recipient": "test@dev.io"})
    assert res.status_code == 400

def test_send_notification_invalid_channel_400(client):
    res = client.post("/api/notifications/send", json={
        "user_id": 1,
        "recipient": "test@dev.io",
        "channel": "carrier_pigeon"
    })
    assert res.status_code == 400
    assert "Channel must be one of" in res.get_json()["error"]

def test_send_notification_direct_content_success(client):
    res = client.post("/api/notifications/send", json={
        "user_id": 1,
        "recipient": "test_direct@dev.io",
        "channel": "email",
        "content": "Direct email content test",
        "subject": "Direct Test"
    })
    assert res.status_code == 202
    data = res.get_json()
    assert data["notification"]["status"] == "Queued"
    assert data["notification"]["content"] == "Direct email content test"

def test_send_notification_with_template_success(client):
    TemplateModel.create_template("welcome_test", "email", "Hello {{ name }}!", subject="Welcome Subject")

    res = client.post("/api/notifications/send", json={
        "user_id": 2,
        "recipient": "test_tmpl@dev.io",
        "channel": "email",
        "template_name": "welcome_test",
        "variables": {"name": "Vee"}
    })
    assert res.status_code == 202
    data = res.get_json()
    assert data["notification"]["content"] == "Hello Vee!"
    assert data["notification"]["subject"] == "Welcome Subject"

def test_send_notification_template_not_found_404(client):
    res = client.post("/api/notifications/send", json={
        "user_id": 1,
        "recipient": "test@dev.io",
        "channel": "email",
        "template_name": "non_existent_template"
    })
    assert res.status_code == 404
    assert "not found" in res.get_json()["error"]

def test_send_notification_template_channel_mismatch_400(client):
    TemplateModel.create_template("sms_only_tmpl", "sms", "SMS Code: {{ code }}")

    res = client.post("/api/notifications/send", json={
        "user_id": 1,
        "recipient": "test@dev.io",
        "channel": "email", # mismatch
        "template_name": "sms_only_tmpl"
    })
    assert res.status_code == 400
    assert "is for channel 'sms'" in res.get_json()["error"]

def test_send_notification_idempotency_key_reuse(client):
    key = "unique_idemp_key_100"
    payload = {
        "user_id": 5,
        "recipient": "idemp@dev.io",
        "channel": "email",
        "content": "First dispatch",
        "idempotency_key": key
    }

    r1 = client.post("/api/notifications/send", json=payload)
    assert r1.status_code == 202
    n1_id = r1.get_json()["notification"]["id"]

    # Re-send with same idempotency key
    r2 = client.post("/api/notifications/send", json=payload)
    assert r2.status_code == 200
    assert "Idempotent request recognized" in r2.get_json()["message"]
    assert r2.get_json()["notification"]["id"] == n1_id

def test_send_notification_missing_content_and_template_400(client):
    res = client.post("/api/notifications/send", json={
        "user_id": 1,
        "recipient": "test@dev.io",
        "channel": "email"
        # missing content & template_name
    })
    assert res.status_code == 400

def test_get_notification_by_id_success(client):
    post_res = client.post("/api/notifications/send", json={
        "user_id": 10,
        "recipient": "get_by_id@dev.io",
        "channel": "email",
        "content": "Get by ID test"
    })
    notif_id = post_res.get_json()["notification"]["id"]

    get_res = client.get(f"/api/notifications/{notif_id}")
    assert get_res.status_code == 200
    assert get_res.get_json()["id"] == notif_id

def test_get_notification_by_id_not_found_404(client):
    res = client.get("/api/notifications/999999")
    assert res.status_code == 404

def test_get_user_notifications_history(client):
    for i in range(3):
        client.post("/api/notifications/send", json={
            "user_id": 77,
            "recipient": f"hist_{i}@dev.io",
            "channel": "email",
            "content": f"History item {i}"
        })

    res = client.get("/api/users/77/notifications")
    assert res.status_code == 200
    items = res.get_json()
    assert len(items) >= 3
    assert items[0]["user_id"] == 77

def test_get_user_notifications_with_limit(client):
    for i in range(5):
        client.post("/api/notifications/send", json={
            "user_id": 88,
            "recipient": f"limit_{i}@dev.io",
            "channel": "email",
            "content": f"Limit item {i}"
        })

    res = client.get("/api/users/88/notifications?limit=2")
    assert res.status_code == 200
    assert len(res.get_json()) == 2

def test_send_sms_notification_route_success(client):
    res = client.post("/api/notifications/send", json={
        "user_id": 12,
        "recipient": "+14155552671",
        "channel": "sms",
        "content": "SMS Alert Content"
    })
    assert res.status_code == 202
    assert res.get_json()["notification"]["channel"] == "sms"

def test_send_webhook_notification_route_success(client):
    res = client.post("/api/notifications/send", json={
        "user_id": 14,
        "recipient": "https://api.test.com/hook",
        "channel": "webhook",
        "content": '{"event": "ping"}'
    })
    assert res.status_code == 202
    assert res.get_json()["notification"]["channel"] == "webhook"

def test_send_notification_rate_limiting_429(client):
    user_id = 999
    # Send up to RATE_LIMIT_PER_MINUTE notifications
    for i in range(Config.RATE_LIMIT_PER_MINUTE):
        r = client.post("/api/notifications/send", json={
            "user_id": user_id,
            "recipient": "rate@dev.io",
            "channel": "email",
            "content": f"Rate test {i}"
        })
        assert r.status_code == 202

    # The 11th request exceeds limit and gets 429
    exceeded_res = client.post("/api/notifications/send", json={
        "user_id": user_id,
        "recipient": "rate@dev.io",
        "channel": "email",
        "content": "Exceeded request"
    })
    assert exceeded_res.status_code == 429
    assert "Rate limit exceeded" in exceeded_res.get_json()["error"]

def test_send_notification_uppercase_channel_handling(client):
    res = client.post("/api/notifications/send", json={
        "user_id": 1,
        "recipient": "upper@dev.io",
        "channel": "EMAIL", # uppercase
        "content": "Uppercase channel test"
    })
    assert res.status_code == 202
    assert res.get_json()["notification"]["channel"] == "email"

def test_send_notification_subject_override(client):
    TemplateModel.create_template("subj_tmpl", "email", "Body text", subject="Default Subject")

    res = client.post("/api/notifications/send", json={
        "user_id": 1,
        "recipient": "override@dev.io",
        "channel": "email",
        "template_name": "subj_tmpl",
        "subject": "Custom Overridden Subject"
    })
    assert res.status_code == 202
    assert res.get_json()["notification"]["subject"] == "Custom Overridden Subject"
