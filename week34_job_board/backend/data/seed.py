import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import init_db, get_db_connection
from app.models.user_model import UserModel
from app.models.job_model import JobModel
from app.models.application_model import ApplicationModel

def seed_database():
    print("[SEED] Initializing database schema...")
    init_db()

    conn = get_db_connection()
    # Check if already seeded
    existing = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()
    if existing["count"] > 0:
        print("[SEED] Database already contains records. Skipping seed.")
        conn.close()
        return

    conn.close()

    print("[SEED] Seeding employer and applicant users...")
    emp1 = UserModel.create_user("techcorp_hr", "hr@techcorp.io", "password123", role="employer", company_name="TechCorp Labs")
    emp2 = UserModel.create_user("cloud_recruiter", "jobs@cloudscale.com", "password123", role="employer", company_name="CloudScale AI")
    
    app1 = UserModel.create_user("vee_coder", "vee@dev.io", "password123", role="applicant")

    print("[SEED] Seeding realistic tech job postings...")
    j1 = JobModel.create_job(
        employer_id=emp1["id"],
        title="Senior Full-Stack Engineer (Python / React)",
        company="TechCorp Labs",
        location="Remote (US / CA)",
        job_type="Remote",
        salary_min=130000,
        salary_max=165000,
        category="Engineering",
        description="We are seeking a talented Senior Full-Stack Engineer to architect scalable WebSockets and microservices.",
        requirements="5+ years experience with Python, Flask, React, and PostgreSQL."
    )

    j2 = JobModel.create_job(
        employer_id=emp1["id"],
        title="Backend Systems Architect",
        company="TechCorp Labs",
        location="New York, NY",
        job_type="Full-time",
        salary_min=150000,
        salary_max=190000,
        category="Engineering",
        description="Lead the design of high-throughput API rate limiters and event streaming data pipelines.",
        requirements="Strong proficiency in Python, Redis, Docker, and distributed systems."
    )

    j3 = JobModel.create_job(
        employer_id=emp2["id"],
        title="AI / ML Platform Engineer",
        company="CloudScale AI",
        location="San Francisco, CA",
        job_type="Full-time",
        salary_min=160000,
        salary_max=210000,
        category="Data Science",
        description="Join CloudScale AI to build infrastructure for training and serving large neural network models.",
        requirements="Experience with PyTorch, CUDA, Python, Kubernetes, and Ray."
    )

    j4 = JobModel.create_job(
        employer_id=emp2["id"],
        title="Frontend Developer (TypeScript / Canvas)",
        company="CloudScale AI",
        location="Remote",
        job_type="Contract",
        salary_min=90000,
        salary_max=120000,
        category="Frontend",
        description="Build interactive UI dashboards and real-time canvas visualization interfaces.",
        requirements="Proficiency in modern HTML5 Canvas, WebGL, TypeScript, and CSS."
    )

    print("[SEED] Seeding sample job application...")
    ApplicationModel.create_application(
        job_id=j1["id"],
        applicant_name="Vee Coder",
        applicant_email="vee@dev.io",
        applicant_id=app1["id"],
        resume_path="/uploads/sample_resume.pdf",
        cover_letter="Excited to apply for the Senior Full-Stack Engineer role! I bring strong experience building real-time Flask and React applications."
    )

    print("[SEED] Database seeding completed successfully! ✨")

if __name__ == "__main__":
    seed_database()
