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

def test_toggle_saved_job_on_and_off(client):
    user = UserModel.create_user("bm_user1", "bm1@test.com", "pass123", role="applicant")
    emp = UserModel.create_user("bm_emp1", "bmemp1@test.com", "pass123", role="employer")
    job = JobModel.create_job(emp["id"], "Security Engineer", "CyberSec", "Remote", "Remote", 120000, 150000, "Engineering", "AppSec Cryptography")

    # Toggle ON
    r1 = client.post(f"/api/users/{user['id']}/saved-jobs", json={"job_id": job["id"]})
    assert r1.status_code == 200
    assert r1.get_json()["saved"] is True

    # Fetch Saved Jobs
    r2 = client.get(f"/api/users/{user['id']}/saved-jobs")
    assert r2.status_code == 200
    jobs = r2.get_json()
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Security Engineer"

    # Toggle OFF
    r3 = client.post(f"/api/users/{user['id']}/saved-jobs", json={"job_id": job["id"]})
    assert r3.status_code == 200
    assert r3.get_json()["saved"] is False

    # Fetch Saved Jobs again
    r4 = client.get(f"/api/users/{user['id']}/saved-jobs")
    assert r4.status_code == 200
    assert len(r4.get_json()) == 0

def test_toggle_saved_job_missing_job_id_400(client):
    user = UserModel.create_user("bm_user2", "bm2@test.com", "pass123", role="applicant")
    res = client.post(f"/api/users/{user['id']}/saved-jobs", json={})
    assert res.status_code == 400
    assert "Job ID is required" in res.get_json()["error"]
