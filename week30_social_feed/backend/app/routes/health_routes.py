from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.route("/health", methods=["GET"])
def health():
    """GET /api/health — liveness check. Returns 200 OK with module identifier."""
    return jsonify({"status": "ok", "module": "week30_social_feed"}), 200
