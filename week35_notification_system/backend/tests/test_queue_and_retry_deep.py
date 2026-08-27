import os
import sys
import time
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.notification_model import NotificationModel
from app.models.user_preference_model import UserPreferenceModel
from app.queues.worker import enqueue_notification_job
from app.queues.task_queue import notification_queue

@pytest.fixture
def app_instance():
    app = create_app()
    app.config["TESTING"] = True
    return app

def test_queue_enqueue_and_sent_status(app_instance):
    n = NotificationModel.create_notification(
        user_id=101,
        recipient="queue101@dev.io",
        channel="email",
        content="Queue test content"
    )
    assert n["status"] == "Queued"
    assert n["attempts"] == 0

    enqueue_notification_job(n["id"])
    time.sleep(0.3)

    updated = NotificationModel.get_by_id(n["id"])
    assert updated["status"] == "Sent"
    assert updated["attempts"] == 1

def test_queue_sms_dispatch(app_instance):
    n = NotificationModel.create_notification(
        user_id=102,
        recipient="+14155552671",
        channel="sms",
        content="SMS queue test"
    )
    enqueue_notification_job(n["id"])
    time.sleep(0.3)

    updated = NotificationModel.get_by_id(n["id"])
    assert updated["status"] == "Sent"

def test_queue_webhook_dispatch(app_instance):
    n = NotificationModel.create_notification(
        user_id=103,
        recipient="https://webhook.dev.io/hook",
        channel="webhook",
        content='{"event": "test"}'
    )
    enqueue_notification_job(n["id"])
    time.sleep(0.3)

    updated = NotificationModel.get_by_id(n["id"])
    assert updated["status"] == "Sent"

def test_queue_invalid_recipient_format_causes_failure(app_instance):
    n = NotificationModel.create_notification(
        user_id=104,
        recipient="invalid_email_format", # Bad recipient format
        channel="email",
        content="Bad recipient test"
    )
    enqueue_notification_job(n["id"])
    time.sleep(1.0) # Wait for retry attempts

    updated = NotificationModel.get_by_id(n["id"])
    assert updated["status"] == "Failed"
    assert "Invalid email address" in updated["error_message"]
    assert updated["attempts"] == 3 # Retry attempts exhausted

def test_queue_opt_out_email_skipping(app_instance):
    UserPreferenceModel.set_user_preferences(user_id=105, email_enabled=False, sms_enabled=True)
    n = NotificationModel.create_notification(
        user_id=105,
        recipient="optout@dev.io",
        channel="email",
        content="Email optout test"
    )
    enqueue_notification_job(n["id"])
    time.sleep(0.3)

    updated = NotificationModel.get_by_id(n["id"])
    assert updated["status"] == "Skipped"
    assert "opted out" in updated["error_message"]

def test_queue_opt_out_webhook_skipping(app_instance):
    UserPreferenceModel.set_user_preferences(user_id=106, webhook_enabled=False)
    n = NotificationModel.create_notification(
        user_id=106,
        recipient="https://optout.dev.io/hook",
        channel="webhook",
        content="Webhook optout test"
    )
    enqueue_notification_job(n["id"])
    time.sleep(0.3)

    updated = NotificationModel.get_by_id(n["id"])
    assert updated["status"] == "Skipped"

def test_queue_unsupported_channel_failure(app_instance):
    # Directly insert raw unsupported channel notification
    n = NotificationModel.create_notification(
        user_id=107,
        recipient="user@dev.io",
        channel="telepathy",
        content="Telepathy content"
    )
    enqueue_notification_job(n["id"])
    time.sleep(0.3)

    updated = NotificationModel.get_by_id(n["id"])
    assert updated["status"] == "Failed"
    assert "Unsupported notification channel" in updated["error_message"]

def test_queue_nonexistent_notification_id(app_instance):
    # Enqueue a bogus notification ID that does not exist in DB
    enqueue_notification_job(9999999)
    time.sleep(0.1)
    # Should handle gracefully without raising unhandled exceptions

def test_queue_singleton_instance_running():
    assert notification_queue._running is True
    assert notification_queue.executor is not None

def test_queue_multiple_concurrent_jobs(app_instance):
    ids = []
    for i in range(5):
        n = NotificationModel.create_notification(
            user_id=200 + i,
            recipient=f"concurrent_{i}@dev.io",
            channel="email",
            content=f"Concurrent job {i}"
        )
        ids.append(n["id"])
        enqueue_notification_job(n["id"])

    time.sleep(0.5)

    for nid in ids:
        assert NotificationModel.get_by_id(nid)["status"] == "Sent"
