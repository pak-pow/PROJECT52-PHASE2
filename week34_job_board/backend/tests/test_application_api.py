import os
import sys
import io
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
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

def test_submit_json_application_success(client):
    emp = UserModel.create_user("emp_app1", "app1@test.com", "pass123", role="employer")
    job = JobModel.create_job(emp["id"], "Full-Stack Engineer", "AppCorp", "Remote", "Remote", 100000, 130000, "Engineering", "Python/React")
    applicant = UserModel.create_user("applicant_app1", "applicant1@test.com", "pass123", role="applicant")

    res = client.post("/api/applications", json={
        "job_id": job["id"],
        "applicant_id": applicant["id"],
        "applicant_name": "Applicant One",
        "applicant_email": "applicant1@test.com",
        "cover_letter": "Enthusiastic full-stack engineer!"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["status"] == "Pending"
    assert data["job_title"] == "Full-Stack Engineer"

def test_submit_application_missing_fields_400(client):
    res = client.post("/api/applications", json={
        "applicant_name": "No Job Applicant"
        # missing job_id and email
    })
    assert res.status_code == 400
    assert "required" in res.get_json()["error"]

def test_submit_application_nonexistent_job_404(client):
    res = client.post("/api/applications", json={
        "job_id": 99999,
        "applicant_name": "Orphan Applicant",
        "applicant_email": "orphan@test.com"
    })
    assert res.status_code == 404
    assert "not found" in res.get_json()["error"]

def test_submit_multipart_pdf_resume_upload(client):
    emp = UserModel.create_user("emp_app2", "app2@test.com", "pass123", role="employer")
    job = JobModel.create_job(emp["id"], "DevOps Engineer", "CloudCorp", "NYC", "Full-time", 110000, 140000, "Engineering", "Docker Kubernetes")

    data = {
        "job_id": str(job["id"]),
        "applicant_name": "Jane Candidate",
        "applicant_email": "jane@test.com",
        "cover_letter": "Resume attached in PDF.",
        "resume": (io.BytesIO(b"%PDF-1.5 Sample Resume Document"), "jane_resume.pdf")
    }

    res = client.post("/api/applications", data=data, content_type="multipart/form-data")
    assert res.status_code == 201
    data = res.get_json()
    assert data["resume_path"].endswith("jane_resume.pdf")

def test_update_application_status_pipeline(client):
    emp = UserModel.create_user("emp_app3", "app3@test.com", "pass123", role="employer")
    job = JobModel.create_job(emp["id"], "Data Analyst", "Analytics LLC", "Remote", "Remote", 75000, 95000, "Data Science", "SQL Tableau")
    app_rec = ApplicationModel.create_application(job["id"], "Bob Analyst", "bob@test.com")

    # Transition to Reviewing
    r1 = client.put(f"/api/applications/{app_rec['id']}/status", json={"status": "Reviewing"})
    assert r1.status_code == 200
    assert r1.get_json()["status"] == "Reviewing"

    # Transition to Interviewing
    r2 = client.put(f"/api/applications/{app_rec['id']}/status", json={"status": "Interviewing"})
    assert r2.status_code == 200
    assert r2.get_json()["status"] == "Interviewing"

    # Transition to Accepted
    r3 = client.put(f"/api/applications/{app_rec['id']}/status", json={"status": "Accepted"})
    assert r3.status_code == 200
    assert r3.get_json()["status"] == "Accepted"

def test_update_status_invalid_value_400(client):
    emp = UserModel.create_user("emp_app4", "app4@test.com", "pass123", role="employer")
    job = JobModel.create_job(emp["id"], "Backend Dev", "DevCorp", "Remote", "Remote", 90000, 120000, "Engineering", "Python")
    app_rec = ApplicationModel.create_application(job["id"], "Charlie Dev", "charlie@test.com")

    res = client.put(f"/api/applications/{app_rec['id']}/status", json={"status": "NOT_A_VALID_STATUS"})
    assert res.status_code == 400
    assert "Status must be one of" in res.get_json()["error"]

def test_get_job_applications_list_for_employer(client):
    emp = UserModel.create_user("emp_app5", "app5@test.com", "pass123", role="employer")
    job = JobModel.create_job(emp["id"], "ML Developer", "AICorp", "SF", "Full-time", 150000, 190000, "Data Science", "PyTorch")

    ApplicationModel.create_application(job["id"], "Candidate A", "a@test.com")
    ApplicationModel.create_application(job["id"], "Candidate B", "b@test.com")

    res = client.get(f"/api/jobs/{job['id']}/applications")
    assert res.status_code == 200
    apps = res.get_json()
    assert len(apps) == 2

def test_get_user_applications_history_for_applicant(client):
    applicant = UserModel.create_user("applicant_app6", "app6@test.com", "pass123", role="applicant")
    emp = UserModel.create_user("emp_app6", "emp6@test.com", "pass123", role="employer")
    job1 = JobModel.create_job(emp["id"], "Job 1", "Co 1", "Remote", "Remote", 80000, 100000, "Engineering", "Desc 1")
    job2 = JobModel.create_job(emp["id"], "Job 2", "Co 2", "NYC", "Full-time", 90000, 110000, "Engineering", "Desc 2")

    ApplicationModel.create_application(job1["id"], "App 6", "app6@test.com", applicant_id=applicant["id"])
    ApplicationModel.create_application(job2["id"], "App 6", "app6@test.com", applicant_id=applicant["id"])

    res = client.get(f"/api/users/{applicant['id']}/applications")
    assert res.status_code == 200
    apps = res.get_json()
    assert len(apps) == 2
    assert apps[0]["applicant_id"] == applicant["id"]
