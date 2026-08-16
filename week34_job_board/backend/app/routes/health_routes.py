from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "week34_job_board",
        "message": "Job Board API is running healthy."
    }), 200
