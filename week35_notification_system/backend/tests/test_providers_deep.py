import pytest
from app.providers.email_provider import EmailNotificationProvider
from app.providers.sms_provider import SMSNotificationProvider
from app.providers.webhook_provider import WebhookNotificationProvider

def test_email_provider_valid_addresses():
    p = EmailNotificationProvider()
    assert p.validate_recipient("user@domain.com") is True
    assert p.validate_recipient("user.name+tag@sub.domain.org") is True
    assert p.validate_recipient("admin@127.0.0.1") is True

def test_email_provider_invalid_addresses():
    p = EmailNotificationProvider()
    assert p.validate_recipient("plainaddress") is False
    assert p.validate_recipient("@domain.com") is False
    assert p.validate_recipient("user@.com") is False
    assert p.validate_recipient("") is False
    assert p.validate_recipient(None) is False

def test_email_provider_send_validation_failure():
    p = EmailNotificationProvider()
    res = p.send("bad_email", "Content")
    assert res["success"] is False
    assert "Invalid email address" in res["error"]

def test_email_provider_send_default_subject():
    p = EmailNotificationProvider()
    res = p.send("user@test.com", "Body content")
    assert res["success"] is True
    assert res["message_id"].startswith("email_")

def test_email_provider_send_custom_subject():
    p = EmailNotificationProvider()
    res = p.send("user@test.com", "Body content", subject="Custom Subj")
    assert res["success"] is True

def test_sms_provider_valid_e164_numbers():
    p = SMSNotificationProvider()
    assert p.validate_recipient("+14155552671") is True
    assert p.validate_recipient("+442071838750") is True
    assert p.validate_recipient("14155552671") is True

def test_sms_provider_invalid_numbers():
    p = SMSNotificationProvider()
    assert p.validate_recipient("123") is False
    assert p.validate_recipient("abcdefghijk") is False
    assert p.validate_recipient("") is False
    assert p.validate_recipient(None) is False

def test_sms_provider_send_validation_failure():
    p = SMSNotificationProvider()
    res = p.send("123", "Short text")
    assert res["success"] is False
    assert "Invalid phone number" in res["error"]

def test_sms_provider_send_success():
    p = SMSNotificationProvider()
    res = p.send("+14155552671", "SMS alert text")
    assert res["success"] is True
    assert res["message_id"].startswith("sms_")

def test_sms_provider_long_content_handling():
    p = SMSNotificationProvider()
    long_msg = "A" * 300
    res = p.send("+14155552671", long_msg)
    assert res["success"] is True

def test_webhook_provider_valid_urls():
    p = WebhookNotificationProvider()
    assert p.validate_recipient("http://localhost:8080/hook") is True
    assert p.validate_recipient("https://api.example.com/v1/webhook?key=123") is True

def test_webhook_provider_invalid_urls():
    p = WebhookNotificationProvider()
    assert p.validate_recipient("ftp://server.com") is False
    assert p.validate_recipient("not_a_url") is False
    assert p.validate_recipient("") is False
    assert p.validate_recipient(None) is False

def test_webhook_provider_send_validation_failure():
    p = WebhookNotificationProvider()
    res = p.send("not_a_url", '{"key": "val"}')
    assert res["success"] is False
    assert "Invalid webhook URL" in res["error"]

def test_webhook_provider_send_success():
    p = WebhookNotificationProvider()
    res = p.send("https://api.myapp.com/events", '{"event": "user.signup"}')
    assert res["success"] is True
    assert res["message_id"].startswith("hook_")

def test_provider_channel_names():
    assert EmailNotificationProvider().channel_name() == "email"
    assert SMSNotificationProvider().channel_name() == "sms"
    assert WebhookNotificationProvider().channel_name() == "webhook"
