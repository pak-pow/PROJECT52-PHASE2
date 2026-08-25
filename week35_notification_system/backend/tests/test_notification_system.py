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

def test_email_provider():
    from app.providers.email_provider import EmailNotificationProvider
    provider = EmailNotificationProvider()
    assert provider.channel_name() == "email"
    assert provider.validate_recipient("vee@dev.io") is True
    assert provider.validate_recipient("invalid_email") is False

    res = provider.send("vee@dev.io", "Hello Email!", subject="Test Email")
    assert res["success"] is True
    assert res["message_id"].startswith("email_")

def test_sms_provider():
    from app.providers.sms_provider import SMSNotificationProvider
    provider = SMSNotificationProvider()
    assert provider.channel_name() == "sms"
    assert provider.validate_recipient("+14155552671") is True
    assert provider.validate_recipient("123") is False

    res = provider.send("+14155552671", "Hello SMS!")
    assert res["success"] is True
    assert res["message_id"].startswith("sms_")

def test_webhook_provider():
    from app.providers.webhook_provider import WebhookNotificationProvider
    provider = WebhookNotificationProvider()
    assert provider.channel_name() == "webhook"
    assert provider.validate_recipient("https://api.myapp.com/webhook") is True
    assert provider.validate_recipient("not_a_url") is False

    res = provider.send("https://api.myapp.com/webhook", '{"event": "alert"}')
    assert res["success"] is True
    assert res["message_id"].startswith("hook_")

def test_template_engine_rendering():
    from app.services.template_engine import TemplateEngine
    tmpl_text = "Welcome to {{ company }}, {{ username }}!"
    rendered = TemplateEngine.render(tmpl_text, {"company": "TechJobs", "username": "Vee"})
    assert rendered == "Welcome to TechJobs, Vee!"

    vars_extracted = TemplateEngine.extract_variables(tmpl_text)
    assert "company" in vars_extracted
    assert "username" in vars_extracted

def test_task_queue_async_execution():
    import time
    from app.queues.worker import enqueue_notification_job

    n = NotificationModel.create_notification(
        user_id=1,
        recipient="queue_test@dev.io",
        channel="email",
        content="Async Queue Execution Test",
        subject="Queue Test"
    )
    assert n["status"] == "Queued"

    enqueue_notification_job(n["id"])
    time.sleep(0.3)

    processed = NotificationModel.get_by_id(n["id"])
    assert processed["status"] == "Sent"

def test_user_opt_out_skipping():
    import time
    from app.queues.worker import enqueue_notification_job

    UserPreferenceModel.set_user_preferences(user_id=88, email_enabled=True, sms_enabled=False)

    n = NotificationModel.create_notification(
        user_id=88,
        recipient="+14155552671",
        channel="sms",
        content="This should be skipped due to opt-out"
    )
    assert n["status"] == "Queued"

    enqueue_notification_job(n["id"])
    time.sleep(0.3)

    processed = NotificationModel.get_by_id(n["id"])
    assert processed["status"] == "Skipped"
    assert "opted out" in processed["error_message"]
