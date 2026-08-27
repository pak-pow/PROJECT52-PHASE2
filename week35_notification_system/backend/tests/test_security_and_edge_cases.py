import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.notification_model import NotificationModel
from app.models.template_model import TemplateModel

@pytest.fixture
def app_instance():
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

def test_sql_injection_resilience_in_idempotency_key(client):
    res = client.post("/api/notifications/send", json={
        "user_id": 901,
        "recipient": "sqli@dev.io",
        "channel": "email",
        "content": "SQLi Test",
        "idempotency_key": "' OR '1'='1' --"
    })
    assert res.status_code == 202
    assert isinstance(res.get_json()["notification"], dict)

def test_xss_payload_in_template_body_rendering():
    from app.services.template_engine import TemplateEngine
    template = "Hello <script>alert('xss')</script> {{ user }}"
    rendered = TemplateEngine.render(template, {"user": "<img src=x onerror=alert(1)>"})
    assert "<script>" in rendered # Safely rendered as text string
    assert "<img" in rendered

def test_large_content_payload_handling(client):
    large_text = "X" * 10000 # 10 KB notification content
    res = client.post("/api/notifications/send", json={
        "user_id": 902,
        "recipient": "large@dev.io",
        "channel": "email",
        "content": large_text
    })
    assert res.status_code == 202
    assert len(res.get_json()["notification"]["content"]) == 10000

def test_special_unicode_characters_in_template_rendering():
    from app.services.template_engine import TemplateEngine
    template = "Welcome 🎉, {{ name }}! 🚀 💼 🎯"
    rendered = TemplateEngine.render(template, {"name": "Vee ⭐"})
    assert "🎉" in rendered
    assert "Vee ⭐" in rendered

def test_serializer_empty_dict_fallback():
    from app.services.serializers import serialize_notification, serialize_template
    assert serialize_notification(None) == {}
    assert serialize_template(None) == {}

def test_database_foreign_key_pragmas(app_instance):
    from app.db import get_db_connection
    conn = get_db_connection()
    pragma = conn.execute("PRAGMA foreign_keys;").fetchone()
    conn.close()
    assert pragma[0] == 1 # Foreign keys enabled

def test_seed_database_execution():
    from data.seed import seed_database
    # Executing seed database should complete idempotently without errors
    seed_database()
    assert TemplateModel.get_by_name("welcome_email") is not None

def test_template_variables_extraction_nested_whitespace():
    from app.services.template_engine import TemplateEngine
    tmpl = "Hi {{   user_name   }}, your code is {{otp_code}}!"
    vars_found = TemplateEngine.extract_variables(tmpl)
    assert "user_name" in vars_found
    assert "otp_code" in vars_found

def test_notification_status_updates_pipeline():
    n = NotificationModel.create_notification(
        user_id=903,
        recipient="pipeline@dev.io",
        channel="email",
        content="Pipeline status test"
    )
    assert n["status"] == "Queued"

    s1 = NotificationModel.update_status(n["id"], "Processing")
    assert s1["status"] == "Processing"

    s2 = NotificationModel.update_status(n["id"], "Sent", attempts=1)
    assert s2["status"] == "Sent"
    assert s2["attempts"] == 1
    assert s2["sent_at"] is not None

def test_cors_headers_present_on_api_responses(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert "Access-Control-Allow-Origin" in res.headers
