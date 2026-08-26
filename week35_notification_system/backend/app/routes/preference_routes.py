from flask import Blueprint, request, jsonify
from app.models.user_preference_model import UserPreferenceModel

preference_bp = Blueprint("preferences", __name__)

@preference_bp.route("/api/preferences/<int:user_id>", methods=["GET"])
def get_user_preferences(user_id):
    prefs = UserPreferenceModel.get_user_preferences(user_id)
    return jsonify(prefs), 200

@preference_bp.route("/api/preferences/<int:user_id>", methods=["PUT"])
def update_user_preferences(user_id):
    data = request.get_json() or {}

    email_enabled = data.get("email_enabled", True)
    sms_enabled = data.get("sms_enabled", True)
    webhook_enabled = data.get("webhook_enabled", True)

    updated = UserPreferenceModel.set_user_preferences(
        user_id=user_id,
        email_enabled=bool(email_enabled),
        sms_enabled=bool(sms_enabled),
        webhook_enabled=bool(webhook_enabled)
    )

    return jsonify({
        "message": "User channel preferences updated.",
        "preferences": updated
    }), 200
