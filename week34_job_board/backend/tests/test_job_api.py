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

def test_create_valid_job_listing(client):
    emp = UserModel.create_user("emp_job1", "job1@test.com", "pass123", role="employer")
    res = client.post("/api/jobs", json={
        "employer_id": emp["id"],
        "title": "Lead Software Architect",
        "company": "Architects Inc",
        "location": "Remote",
        "job_type": "Remote",
        "salary_min": 160000,
        "salary_max": 200000,
        "category": "Engineering",
        "description": "Architect cloud-native microservices.",
        "requirements": "Kubernetes, Python, Go"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["title"] == "Lead Software Architect"
    assert data["salary_min"] == 160000

def test_create_job_missing_required_fields_400(client):
    res = client.post("/api/jobs", json={
        "employer_id": 1,
        "title": "Missing Info Job"
        # missing company, location, description
    })
    assert res.status_code == 400
    assert "required" in res.get_json()["error"]

def test_get_job_by_id_success(client):
    emp = UserModel.create_user("emp_job2", "job2@test.com", "pass123", role="employer")
    job = JobModel.create_job(emp["id"], "UI/UX Designer", "Design Studio", "New York", "Full-time", 85000, 110000, "Design", "Design Figma prototypes.")

    res = client.get(f"/api/jobs/{job['id']}")
    assert res.status_code == 200
    assert res.get_json()["title"] == "UI/UX Designer"

def test_get_job_by_id_not_found_404(client):
    res = client.get("/api/jobs/88888")
    assert res.status_code == 404
    assert "not found" in res.get_json()["error"]

def test_filter_jobs_by_keyword(client):
    emp = UserModel.create_user("emp_job3", "job3@test.com", "pass123", role="employer")
    JobModel.create_job(emp["id"], "PySpark Data Engineer", "DataCorp", "Remote", "Remote", 120000, 150000, "Data Science", "PySpark and AWS Glue")
    JobModel.create_job(emp["id"], "iOS Developer", "MobileApp Inc", "Austin", "Full-time", 100000, 130000, "Engineering", "Swift and SwiftUI")

    res = client.get("/api/jobs?keyword=PySpark")
    assert res.status_code == 200
    jobs = res.get_json()
    assert len(jobs) == 1
    assert jobs[0]["title"] == "PySpark Data Engineer"

def test_filter_jobs_by_location_and_type(client):
    emp = UserModel.create_user("emp_job4", "job4@test.com", "pass123", role="employer")
    JobModel.create_job(emp["id"], "Backend Engineer", "Tech1", "San Francisco, CA", "Full-time", 140000, 180000, "Engineering", "Python")
    JobModel.create_job(emp["id"], "Frontend Engineer", "Tech2", "Remote", "Remote", 110000, 140000, "Frontend", "React")

    res = client.get("/api/jobs?location=San%20Francisco&type=Full-time")
    assert res.status_code == 200
    jobs = res.get_json()
    assert len(jobs) == 1
    assert jobs[0]["company"] == "Tech1"

def test_filter_jobs_by_min_salary(client):
    emp = UserModel.create_user("emp_job5", "job5@test.com", "pass123", role="employer")
    JobModel.create_job(emp["id"], "Junior Dev", "JuniorCo", "Remote", "Full-time", 60000, 80000, "Engineering", "HTML CSS")
    JobModel.create_job(emp["id"], "Principal Dev", "BigCo", "Remote", "Full-time", 180000, 220000, "Engineering", "Architecture")

    res = client.get("/api/jobs?min_salary=150000")
    assert res.status_code == 200
    jobs = res.get_json()
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Principal Dev"

def test_update_job_listing_success(client):
    emp = UserModel.create_user("emp_job6", "job6@test.com", "pass123", role="employer")
    job = JobModel.create_job(emp["id"], "Old Title", "Old Company", "Remote", "Full-time", 70000, 90000, "Engineering", "Old desc")

    res = client.put(f"/api/jobs/{job['id']}", json={
        "title": "Updated Title",
        "salary_max": 110000
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["title"] == "Updated Title"
    assert data["salary_max"] == 110000

def test_delete_job_listing_success(client):
    emp = UserModel.create_user("emp_job7", "job7@test.com", "pass123", role="employer")
    job = JobModel.create_job(emp["id"], "Temp Job", "Temp Co", "Remote", "Contract", 50000, 70000, "Engineering", "Temp desc")

    del_res = client.delete(f"/api/jobs/{job['id']}")
    assert del_res.status_code == 200
    assert "deleted" in del_res.get_json()["message"]

    get_res = client.get(f"/api/jobs/{job['id']}")
    assert get_res.status_code == 404
