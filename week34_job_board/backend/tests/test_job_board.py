import os
import sys
import pytest

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.db import init_db
from app.models.user_model import UserModel
from app.models.job_model import JobModel
from app.models.application_model import ApplicationModel

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
    assert data["service"] == "week34_job_board"

def test_user_registration_and_login(client):
    reg_res = client.post("/api/auth/register", json={
        "username": "test_emp",
        "email": "emp@test.com",
        "password": "secret_pass_123",
        "role": "employer",
        "company_name": "TestCorp"
    })
    assert reg_res.status_code == 201
    data = reg_res.get_json()
    assert data["user"]["email"] == "emp@test.com"

    login_res = client.post("/api/auth/login", json={
        "email": "emp@test.com",
        "password": "secret_pass_123"
    })
    assert login_res.status_code == 200
    user_data = login_res.get_json()["user"]
    assert user_data["username"] == "test_emp"

def test_job_creation_and_search_filtering(client):
    emp = UserModel.create_user("hr_boss", "boss@corp.com", "pass123", role="employer")
    
    j1 = client.post("/api/jobs", json={
        "employer_id": emp["id"],
        "title": "Senior Python Developer",
        "company": "Corp LLC",
        "location": "Remote",
        "job_type": "Remote",
        "salary_min": 100000,
        "salary_max": 140000,
        "category": "Engineering",
        "description": "Python API development"
    }).get_json()

    search_res = client.get("/api/jobs?keyword=Python&type=Remote")
    assert search_res.status_code == 200
    jobs = search_res.get_json()
    assert len(jobs) >= 1
    assert jobs[0]["title"] == "Senior Python Developer"

def test_application_submission_and_status_update(client):
    emp = UserModel.create_user("emp_unit", "empunit@corp.com", "pass123", role="employer")
    app_user = UserModel.create_user("applicant_unit", "appunit@dev.com", "pass123", role="applicant")
    
    job = JobModel.create_job(emp["id"], "React Engineer", "UI Corp", "New York", "Full-time", 80000, 110000, "Frontend", "Building React UI")

    app_res = client.post("/api/applications", json={
        "job_id": job["id"],
        "applicant_id": app_user["id"],
        "applicant_name": "Applicant Unit",
        "applicant_email": "appunit@dev.com",
        "cover_letter": "I love React!"
    })
    assert app_res.status_code == 201
    app_data = app_res.get_json()
    assert app_data["status"] == "Pending"

    status_res = client.put(f"/api/applications/{app_data['id']}/status", json={"status": "Interviewing"})
    assert status_res.status_code == 200
    assert status_res.get_json()["status"] == "Interviewing"
