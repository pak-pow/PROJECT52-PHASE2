from flask import Blueprint, request, jsonify
from app.services.api_key_service import api_key_manager, TIER_LIMITS

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/auth/api-key", methods=["POST"])
def issue_api_key():
    data = request.get_json(silent=True) or request.form
    tier = (data.get("tier") or "free").lower()
    
    if tier not in TIER_LIMITS:
        return jsonify({
            "error": f"Invalid tier. Must be one of: {list(TIER_LIMITS.keys())}"
        }), 400

    new_key = api_key_manager.generate_key(tier)
    limit, window = TIER_LIMITS[tier]

    return jsonify({
        "api_key": new_key,
        "tier": tier,
        "rate_limit": {
            "capacity": limit,
            "window_seconds": window,
            "requests_per_minute": limit
        },
        "message": f"Issued new {tier.upper()} tier API Key successfully."
    }), 201

@auth_bp.route("/api/auth/api-key/status", methods=["GET"])
def check_key_status():
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return jsonify({"error": "Header 'X-API-Key' is required."}), 400

    tier = api_key_manager.get_tier(api_key)
    limit, window = api_key_manager.get_tier_limit(api_key)

    return jsonify({
        "api_key": api_key,
        "tier": tier,
        "capacity": limit,
        "window_seconds": window
    }), 200
