from flask import Blueprint, request, jsonify
from app.models.job_model import JobModel
from app.services.serializers import serialize_job

job_bp = Blueprint("jobs", __name__)

@job_bp.route("/api/jobs", methods=["GET"])
def get_jobs():
    keyword = request.args.get("keyword")
    location = request.args.get("location")
    job_type = request.args.get("type")
    category = request.args.get("category")
    min_salary = request.args.get("min_salary", 0)

    jobs = JobModel.get_all(keyword=keyword, location=location, job_type=job_type, category=category, min_salary=min_salary)
    return jsonify([serialize_job(j) for j in jobs]), 200

@job_bp.route("/api/jobs/<int:job_id>", methods=["GET"])
def get_job_by_id(job_id: int):
    job = JobModel.get_by_id(job_id)
    if not job:
        return jsonify({"error": "Job listing not found."}), 404
    return jsonify(serialize_job(job)), 200

@job_bp.route("/api/jobs", methods=["POST"])
def create_job():
    data = request.get_json() or {}
    employer_id = data.get("employer_id")
    title = data.get("title", "").strip()
    company = data.get("company", "").strip()
    location = data.get("location", "").strip()
    job_type = data.get("job_type", "Full-time").strip()
    salary_min = data.get("salary_min", 0)
    salary_max = data.get("salary_max", 0)
    category = data.get("category", "Engineering").strip()
    description = data.get("description", "").strip()
    requirements = data.get("requirements", "").strip()

    if not employer_id or not title or not company or not location or not description:
        return jsonify({"error": "Employer ID, title, company, location, and description are required."}), 400

    job = JobModel.create_job(
        employer_id=employer_id,
        title=title,
        company=company,
        location=location,
        job_type=job_type,
        salary_min=int(salary_min),
        salary_max=int(salary_max),
        category=category,
        description=description,
        requirements=requirements
    )
    return jsonify(serialize_job(job)), 201

@job_bp.route("/api/jobs/<int:job_id>", methods=["PUT"])
def update_job(job_id: int):
    data = request.get_json() or {}
    job = JobModel.get_by_id(job_id)
    if not job:
        return jsonify({"error": "Job listing not found."}), 404

    updated_job = JobModel.update_job(job_id, **data)
    return jsonify(serialize_job(updated_job)), 200

@job_bp.route("/api/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id: int):
    job = JobModel.get_by_id(job_id)
    if not job:
        return jsonify({"error": "Job listing not found."}), 404

    success = JobModel.delete_job(job_id)
    if success:
        return jsonify({"message": "Job listing deleted successfully."}), 200
    return jsonify({"error": "Failed to delete job listing."}), 500
