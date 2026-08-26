from flask import Blueprint, request, jsonify
from app.models.template_model import TemplateModel
from app.services.serializers import serialize_template

template_bp = Blueprint("templates", __name__)

@template_bp.route("/api/templates", methods=["GET"])
def list_templates():
    templates = TemplateModel.get_all()
    return jsonify([serialize_template(t) for t in templates]), 200

@template_bp.route("/api/templates/<name>", methods=["GET"])
def get_template(name):
    tmpl = TemplateModel.get_by_name(name)
    if not tmpl:
        return jsonify({"error": f"Template '{name}' not found."}), 404
    return jsonify(serialize_template(tmpl)), 200

@template_bp.route("/api/templates", methods=["POST"])
def create_template():
    data = request.get_json() or {}

    name = data.get("name")
    channel = data.get("channel")
    body_template = data.get("body_template")
    subject = data.get("subject")

    if not name or not channel or not body_template:
        return jsonify({"error": "Fields 'name', 'channel', and 'body_template' are required."}), 400

    channel_clean = str(channel).lower()
    if channel_clean not in ["email", "sms", "webhook"]:
        return jsonify({"error": "Channel must be one of 'email', 'sms', or 'webhook'."}), 400

    existing = TemplateModel.get_by_name(name)
    if existing:
        return jsonify({"error": f"Template name '{name}' already exists."}), 409

    tmpl = TemplateModel.create_template(
        name=name,
        channel=channel_clean,
        body_template=body_template,
        subject=subject
    )

    return jsonify({
        "message": "Notification template created successfully.",
        "template": serialize_template(tmpl)
    }), 201
