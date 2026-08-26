import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.template_model import TemplateModel

@pytest.fixture
def app_instance():
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

def test_list_templates_success(client):
    res = client.get("/api/templates")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_create_template_email_success(client):
    res = client.post("/api/templates", json={
        "name": "password_reset_email",
        "channel": "email",
        "subject": "Reset your password",
        "body_template": "Click here to reset your password: {{ link }}"
    })
    assert res.status_code == 201
    data = res.get_json()["template"]
    assert data["name"] == "password_reset_email"
    assert data["channel"] == "email"

def test_create_template_sms_success(client):
    res = client.post("/api/templates", json={
        "name": "otp_verification_sms",
        "channel": "sms",
        "body_template": "Your login OTP is {{ code }}. Valid for 5 minutes."
    })
    assert res.status_code == 201
    assert res.get_json()["template"]["channel"] == "sms"

def test_create_template_webhook_success(client):
    res = client.post("/api/templates", json={
        "name": "order_created_webhook",
        "channel": "webhook",
        "body_template": '{"event": "order_created", "order_id": "{{ order_id }}"}'
    })
    assert res.status_code == 201
    assert res.get_json()["template"]["channel"] == "webhook"

def test_create_template_missing_name_400(client):
    res = client.post("/api/templates", json={
        "channel": "email",
        "body_template": "Body text"
    })
    assert res.status_code == 400
    assert "required" in res.get_json()["error"]

def test_create_template_missing_channel_400(client):
    res = client.post("/api/templates", json={
        "name": "no_chan_tmpl",
        "body_template": "Body text"
    })
    assert res.status_code == 400

def test_create_template_missing_body_400(client):
    res = client.post("/api/templates", json={
        "name": "no_body_tmpl",
        "channel": "email"
    })
    assert res.status_code == 400

def test_create_template_invalid_channel_400(client):
    res = client.post("/api/templates", json={
        "name": "invalid_chan_tmpl",
        "channel": "telepathy",
        "body_template": "Body"
    })
    assert res.status_code == 400
    assert "Channel must be one of" in res.get_json()["error"]

def test_create_template_duplicate_name_409(client):
    client.post("/api/templates", json={
        "name": "dup_template_name",
        "channel": "email",
        "body_template": "First"
    })
    res = client.post("/api/templates", json={
        "name": "dup_template_name",
        "channel": "email",
        "body_template": "Second"
    })
    assert res.status_code == 409
    assert "already exists" in res.get_json()["error"]

def test_get_template_by_name_success(client):
    client.post("/api/templates", json={
        "name": "fetch_me_tmpl",
        "channel": "email",
        "body_template": "Fetch body"
    })
    res = client.get("/api/templates/fetch_me_tmpl")
    assert res.status_code == 200
    assert res.get_json()["name"] == "fetch_me_tmpl"

def test_get_template_by_name_not_found_404(client):
    res = client.get("/api/templates/nonexistent_tmpl_xyz")
    assert res.status_code == 404
    assert "not found" in res.get_json()["error"]

def test_create_template_lowercase_channel_normalization(client):
    res = client.post("/api/templates", json={
        "name": "upper_chan_tmpl",
        "channel": "EMAIL", # uppercase
        "body_template": "Body text"
    })
    assert res.status_code == 201
    assert res.get_json()["template"]["channel"] == "email"

def test_template_model_get_all_ordering():
    TemplateModel.create_template("b_tmpl", "email", "B")
    TemplateModel.create_template("a_tmpl", "email", "A")
    all_tmpls = TemplateModel.get_all()
    names = [t["name"] for t in all_tmpls]
    assert names == sorted(names)

def test_template_subject_optional_for_sms():
    tmpl = TemplateModel.create_template("sms_no_subj", "sms", "SMS text without subject")
    assert tmpl["subject"] is None

def test_template_subject_rendering():
    tmpl = TemplateModel.create_template("subj_render_tmpl", "email", "Body", subject="Hi {{ name }}")
    assert tmpl["subject"] == "Hi {{ name }}"
