import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user_model import UserModel

@pytest.fixture
def app_instance():
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

def test_successful_applicant_registration(client):
    res = client.post("/api/auth/register", json={
        "username": "applicant_test1",
        "email": "applicant1@test.com",
        "password": "securepassword123",
        "role": "applicant"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["user"]["role"] == "applicant"
    assert data["user"]["email"] == "applicant1@test.com"

def test_successful_employer_registration(client):
    res = client.post("/api/auth/register", json={
        "username": "employer_test1",
        "email": "employer1@test.com",
        "password": "securepassword123",
        "role": "employer",
        "company_name": "Apex Innovations"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["user"]["role"] == "employer"
    assert data["user"]["company_name"] == "Apex Innovations"

def test_register_missing_required_fields_400(client):
    res = client.post("/api/auth/register", json={
        "username": "incomplete_user"
        # missing email and password
    })
    assert res.status_code == 400
    assert "required" in res.get_json()["error"]

def test_register_invalid_role_400(client):
    res = client.post("/api/auth/register", json={
        "username": "bad_role_user",
        "email": "badrole@test.com",
        "password": "password123",
        "role": "superadmin" # invalid role
    })
    assert res.status_code == 400
    assert "Role must be" in res.get_json()["error"]

def test_register_duplicate_email_409(client):
    client.post("/api/auth/register", json={
        "username": "orig_user",
        "email": "same_email@test.com",
        "password": "password123"
    })
    res = client.post("/api/auth/register", json={
        "username": "dup_user",
        "email": "same_email@test.com",
        "password": "password123"
    })
    assert res.status_code == 409
    assert "already exists" in res.get_json()["error"]

def test_login_success(client):
    client.post("/api/auth/register", json={
        "username": "login_user",
        "email": "login@test.com",
        "password": "correct_pass"
    })
    res = client.post("/api/auth/login", json={
        "email": "login@test.com",
        "password": "correct_pass"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["user"]["username"] == "login_user"
    assert "password_hash" not in data["user"]

def test_login_invalid_password_401(client):
    client.post("/api/auth/register", json={
        "username": "auth_user",
        "email": "authuser@test.com",
        "password": "valid_password"
    })
    res = client.post("/api/auth/login", json={
        "email": "authuser@test.com",
        "password": "WRONG_PASSWORD"
    })
    assert res.status_code == 401
    assert "Invalid email or password" in res.get_json()["error"]

def test_login_nonexistent_email_401(client):
    res = client.post("/api/auth/login", json={
        "email": "nonexistent@test.com",
        "password": "anypassword"
    })
    assert res.status_code == 401
