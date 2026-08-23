from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "week35_notification_system",
        "message": "Notification System API & Queue Manager operational."
    }), 200
