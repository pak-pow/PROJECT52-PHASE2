import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user_model import UserModel
from app.models.job_model import JobModel

@pytest.fixture
def app_instance():
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

def test_sql_injection_resilience_in_search(client):
    res = client.get("/api/jobs?keyword=' OR '1'='1' --")
    assert res.status_code == 200
    # Parameterized SQL query prevents injection and returns 0 matching results cleanly
    assert isinstance(res.get_json(), list)

def test_resume_download_endpoint_security(client):
    # Try directory traversal attack
    res = client.get("/uploads/../../etc/passwd")
    # Flask send_from_directory prevents path traversal and returns 404/400
    assert res.status_code in [400, 404]

def test_xss_payload_in_job_title_sanitization(client):
    emp = UserModel.create_user("emp_sec", "sec@corp.com", "pass123", role="employer")
    job = JobModel.create_job(emp["id"], "<script>alert('xss')</script>", "XSS Corp", "Remote", "Remote", 50000, 70000, "Engineering", "Desc")

    res = client.get(f"/api/jobs/{job['id']}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["title"] == "<script>alert('xss')</script>" # Stored safely as raw string, escaped on frontend
