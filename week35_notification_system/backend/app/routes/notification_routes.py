from flask import Blueprint, request, jsonify
from app.models.notification_model import NotificationModel
from app.models.template_model import TemplateModel
from app.models.user_preference_model import UserPreferenceModel
from app.services.template_engine import TemplateEngine
from app.services.serializers import serialize_notification
from app.queues.worker import enqueue_notification_job
from app.config.settings import Config

notification_bp = Blueprint("notifications", __name__)

@notification_bp.route("/api/notifications/send", methods=["POST"])
def send_notification():
    data = request.get_json() or {}

    user_id = data.get("user_id")
    recipient = data.get("recipient")
    channel = data.get("channel")
    template_name = data.get("template_name")
    variables = data.get("variables", {})
    idempotency_key = data.get("idempotency_key")
    direct_content = data.get("content")
    subject_override = data.get("subject")

    if not user_id or not recipient or not channel:
        return jsonify({"error": "Fields 'user_id', 'recipient', and 'channel' are required."}), 400

    channel_clean = str(channel).lower()
    if channel_clean not in ["email", "sms", "webhook"]:
        return jsonify({"error": "Channel must be one of 'email', 'sms', or 'webhook'."}), 400

    # 1. Idempotency Check
    if idempotency_key:
        existing = NotificationModel.get_by_idempotency_key(idempotency_key)
        if existing:
            return jsonify({
                "message": "Idempotent request recognized. Returning existing record.",
                "notification": serialize_notification(existing)
            }), 200

    # 2. Rate Limiting Check
    recent_count = NotificationModel.count_recent_user_notifications(user_id, minutes=1)
    if recent_count >= Config.RATE_LIMIT_PER_MINUTE:
        return jsonify({"error": f"Rate limit exceeded. Maximum {Config.RATE_LIMIT_PER_MINUTE} notifications per minute."}), 429

    # 3. Determine Content and Subject
    final_content = direct_content or ""
    final_subject = subject_override or None

    if template_name:
        tmpl = TemplateModel.get_by_name(template_name)
        if not tmpl:
            return jsonify({"error": f"Notification template '{template_name}' not found."}), 404

        if tmpl["channel"].lower() != channel_clean:
            return jsonify({"error": f"Template '{template_name}' is for channel '{tmpl['channel']}', not '{channel_clean}'."}), 400

        rendered_body = TemplateEngine.render(tmpl["body_template"], variables)
        final_content = rendered_body

        if tmpl.get("subject") and not final_subject:
            final_subject = TemplateEngine.render(tmpl["subject"], variables)

    if not final_content:
        return jsonify({"error": "Notification content or valid template_name is required."}), 400

    # 4. Create Notification Record (Queued)
    notif = NotificationModel.create_notification(
        user_id=user_id,
        recipient=recipient,
        channel=channel_clean,
        content=final_content,
        subject=final_subject,
        template_name=template_name,
        variables=variables,
        idempotency_key=idempotency_key
    )

    # 5. Enqueue Async Worker Job
    enqueue_notification_job(notif["id"])

    return jsonify({
        "message": "Notification enqueued for dispatch.",
        "notification": serialize_notification(notif)
    }), 202

@notification_bp.route("/api/notifications/<int:notif_id>", methods=["GET"])
def get_notification(notif_id):
    notif = NotificationModel.get_by_id(notif_id)
    if not notif:
        return jsonify({"error": "Notification record not found."}), 404
    return jsonify(serialize_notification(notif)), 200

@notification_bp.route("/api/users/<int:user_id>/notifications", methods=["GET"])
def get_user_notifications(user_id):
    limit = request.args.get("limit", 50, type=int)
    notifs = NotificationModel.get_user_notifications(user_id, limit=limit)
    return jsonify([serialize_notification(n) for n in notifs]), 200
