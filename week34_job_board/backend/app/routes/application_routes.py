import os
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, send_from_directory
from app.config.settings import Config
from app.models.application_model import ApplicationModel
from app.models.job_model import JobModel
from app.services.serializers import serialize_application, serialize_job

application_bp = Blueprint("applications", __name__)

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@application_bp.route("/api/applications", methods=["POST"])
def submit_application():
    # Supports JSON payload or multipart/form-data with resume file
    job_id = request.form.get("job_id")
    applicant_name = request.form.get("applicant_name", "").strip()
    applicant_email = request.form.get("applicant_email", "").strip().lower()
    applicant_id = request.form.get("applicant_id")
    cover_letter = request.form.get("cover_letter", "").strip()

    if not job_id and request.is_json:
        data = request.get_json() or {}
        job_id = data.get("job_id")
        applicant_name = data.get("applicant_name", "").strip()
        applicant_email = data.get("applicant_email", "").strip().lower()
        applicant_id = data.get("applicant_id")
        cover_letter = data.get("cover_letter", "").strip()

    if not job_id or not applicant_name or not applicant_email:
        return jsonify({"error": "Job ID, applicant name, and email are required."}), 400

    job = JobModel.get_by_id(int(job_id))
    if not job:
        return jsonify({"error": "Target job listing not found."}), 404

    resume_path = None
    if "resume" in request.files:
        file = request.files["resume"]
        if file and file.filename and allowed_file(file.filename):
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(f"app_{job_id}_{file.filename}")
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(filepath)
            resume_path = f"/uploads/{filename}"

    app_record = ApplicationModel.create_application(
        job_id=int(job_id),
        applicant_name=applicant_name,
        applicant_email=applicant_email,
        applicant_id=int(applicant_id) if applicant_id else None,
        resume_path=resume_path,
        cover_letter=cover_letter
    )
    return jsonify(serialize_application(app_record)), 201

@application_bp.route("/api/jobs/<int:job_id>/applications", methods=["GET"])
def get_job_applications(job_id: int):
    apps = ApplicationModel.get_by_job(job_id)
    return jsonify([serialize_application(a) for a in apps]), 200

@application_bp.route("/api/applications/<int:app_id>/status", methods=["PUT"])
def update_application_status(app_id: int):
    data = request.get_json() or {}
    status = data.get("status", "").strip()

    valid_statuses = ["Pending", "Reviewing", "Interviewing", "Accepted", "Rejected"]
    if status not in valid_statuses:
        return jsonify({"error": f"Status must be one of {valid_statuses}."}), 400

    updated = ApplicationModel.update_status(app_id, status)
    if not updated:
        return jsonify({"error": "Application not found."}), 404
    return jsonify(serialize_application(updated)), 200

@application_bp.route("/api/users/<int:user_id>/applications", methods=["GET"])
def get_applicant_applications(user_id: int):
    apps = ApplicationModel.get_by_applicant(user_id)
    return jsonify([serialize_application(a) for a in apps]), 200

@application_bp.route("/api/users/<int:user_id>/saved-jobs", methods=["GET", "POST"])
def manage_saved_jobs(user_id: int):
    if request.method == "POST":
        data = request.get_json() or {}
        job_id = data.get("job_id")
        if not job_id:
            return jsonify({"error": "Job ID is required."}), 400
        res = ApplicationModel.toggle_saved_job(user_id, int(job_id))
        return jsonify(res), 200

    saved_jobs = ApplicationModel.get_saved_jobs(user_id)
    return jsonify([serialize_job(j) for j in saved_jobs]), 200

@application_bp.route("/uploads/<path:filename>", methods=["GET"])
def download_resume(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)
