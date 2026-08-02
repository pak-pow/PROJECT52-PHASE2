from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "week32_rate_limiter",
        "engine": "Token Bucket & Sliding Window Log",
        "version": "1.0.0"
    }), 200
