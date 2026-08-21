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

def test_job_not_found_404(client):
    res = client.get("/api/jobs/99999")
    assert res.status_code == 404
    data = res.get_json()
    assert "error" in data

def test_invalid_status_update_400(client):
    emp = UserModel.create_user("emp_bad_status", "badstatus@corp.com", "pass123", role="employer")
    job = JobModel.create_job(emp["id"], "DevOps Engineer", "DevOps Inc", "Remote", "Full-time", 90000, 120000, "Engineering", "CI/CD Pipelines")
    app_record = ApplicationModel.create_application(job["id"], "Candidate A", "cand@test.com")

    res = client.put(f"/api/applications/{app_record['id']}/status", json={"status": "INVALID_STATUS"})
    assert res.status_code == 400
    assert "error" in res.get_json()

def test_saved_jobs_bookmarking(client):
    user = UserModel.create_user("bookmark_user", "bm@test.com", "pass123", role="applicant")
    emp = UserModel.create_user("emp_bm", "empbm@test.com", "pass123", role="employer")
    job = JobModel.create_job(emp["id"], "Data Engineer", "DataCorp", "Chicago", "Full-time", 110000, 140000, "Data Science", "SQL & PySpark")

    # Bookmark job
    post_res = client.post(f"/api/users/{user['id']}/saved-jobs", json={"job_id": job["id"]})
    assert post_res.status_code == 200
    assert post_res.get_json()["saved"] is True

    # Get saved jobs
    get_res = client.get(f"/api/users/{user['id']}/saved-jobs")
    assert get_res.status_code == 200
    saved_list = get_res.get_json()
    assert len(saved_list) == 1
    assert saved_list[0]["title"] == "Data Engineer"

    # Un-bookmark job
    unbm_res = client.post(f"/api/users/{user['id']}/saved-jobs", json={"job_id": job["id"]})
    assert unbm_res.status_code == 200
    assert unbm_res.get_json()["saved"] is False

def test_resume_file_upload_application(client):
    import io
    emp = UserModel.create_user("emp_upload", "upload@corp.com", "pass123", role="employer")
    job = JobModel.create_job(emp["id"], "Full-Stack Dev", "WebCorp", "Remote", "Remote", 95000, 125000, "Engineering", "Flask & React")

    data = {
        "job_id": str(job["id"]),
        "applicant_name": "Test Applicant",
        "applicant_email": "applicant@upload.com",
        "cover_letter": "Please see attached resume.",
        "resume": (io.BytesIO(b"%PDF-1.4 sample resume content"), "my_resume.pdf")
    }

    res = client.post("/api/applications", data=data, content_type="multipart/form-data")
    assert res.status_code == 201
    app_data = res.get_json()
    assert app_data["resume_path"].endswith("my_resume.pdf")

def test_duplicate_email_registration_409(client):
    client.post("/api/auth/register", json={
        "username": "user1",
        "email": "duplicate@test.com",
        "password": "password123"
    })
    res2 = client.post("/api/auth/register", json={
        "username": "user2",
        "email": "duplicate@test.com",
        "password": "password123"
    })
    assert res2.status_code == 409
    assert "already exists" in res2.get_json()["error"]

def test_invalid_login_credentials_401(client):
    client.post("/api/auth/register", json={
        "username": "user_auth",
        "email": "auth@test.com",
        "password": "correct_password"
    })
    res = client.post("/api/auth/login", json={
        "email": "auth@test.com",
        "password": "WRONG_PASSWORD"
    })
    assert res.status_code == 401
    assert "Invalid email or password" in res.get_json()["error"]

def test_job_deletion_workflow(client):
    emp = UserModel.create_user("emp_del", "del@corp.com", "pass123", role="employer")
    job = JobModel.create_job(emp["id"], "QA Automation Engineer", "QACorp", "Remote", "Full-time", 80000, 100000, "Engineering", "Pytest & Selenium")

    del_res = client.delete(f"/api/jobs/{job['id']}")
    assert del_res.status_code == 200
    assert del_res.get_json()["message"] == "Job listing deleted successfully."

    get_res = client.get(f"/api/jobs/{job['id']}")
    assert get_res.status_code == 404

def test_job_creation_missing_fields_400(client):
    res = client.post("/api/jobs", json={
        "employer_id": 1,
        "title": "Incomplete Job"
        # missing company, location, description
    })
    assert res.status_code == 400
    assert "required" in res.get_json()["error"]

def test_applicant_applications_history_list(client):
    emp = UserModel.create_user("emp_hist", "hist@corp.com", "pass123", role="employer")
    applicant = UserModel.create_user("applicant_hist", "apphist@dev.com", "pass123", role="applicant")

    job1 = JobModel.create_job(emp["id"], "Node.js Developer", "Backend LLC", "Remote", "Remote", 100000, 130000, "Engineering", "Express & Mongo")
    job2 = JobModel.create_job(emp["id"], "Python Developer", "Data Inc", "NYC", "Full-time", 110000, 140000, "Engineering", "FastAPI")

    ApplicationModel.create_application(job1["id"], "Applicant Hist", "apphist@dev.com", applicant_id=applicant["id"], cover_letter="App 1")
    ApplicationModel.create_application(job2["id"], "Applicant Hist", "apphist@dev.com", applicant_id=applicant["id"], cover_letter="App 2")

    res = client.get(f"/api/users/{applicant['id']}/applications")
    assert res.status_code == 200
    apps_list = res.get_json()
    assert len(apps_list) == 2
    assert apps_list[0]["applicant_id"] == applicant["id"]
