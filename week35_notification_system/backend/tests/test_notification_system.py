import os
import sys
import pytest

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.template_model import TemplateModel
from app.models.user_preference_model import UserPreferenceModel
from app.models.notification_model import NotificationModel

@pytest.fixture
def app_instance():
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "week35_notification_system"

def test_template_model_crud():
    tmpl = TemplateModel.create_template("test_welcome", "email", "Hello {{ name }}!", subject="Welcome")
    assert tmpl["name"] == "test_welcome"
    assert tmpl["channel"] == "email"

    fetched = TemplateModel.get_by_name("test_welcome")
    assert fetched["id"] == tmpl["id"]

def test_user_preference_model():
    prefs = UserPreferenceModel.get_user_preferences(user_id=99)
    assert prefs["email_enabled"] is True

    updated = UserPreferenceModel.set_user_preferences(user_id=99, email_enabled=True, sms_enabled=False)
    assert updated["sms_enabled"] is False

    assert UserPreferenceModel.is_channel_enabled(99, "email") is True
    assert UserPreferenceModel.is_channel_enabled(99, "sms") is False

def test_notification_model_crud():
    n = NotificationModel.create_notification(
        user_id=10,
        recipient="user10@test.com",
        channel="email",
        content="Test Notification Content",
        subject="Subject Test",
        idempotency_key="idemp_101"
    )
    assert n["status"] == "Queued"
    assert n["idempotency_key"] == "idemp_101"

    updated = NotificationModel.update_status(n["id"], "Sent")
    assert updated["status"] == "Sent"
    assert updated["sent_at"] is not None
