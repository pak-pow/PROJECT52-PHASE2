from flask import Blueprint, request, jsonify
from app.models.service_model import get_all_services, get_service_by_id
from app.models.provider_model import get_providers_for_service
from app.services.serializers import serialize_service, serialize_provider

service_bp = Blueprint("services", __name__)


@service_bp.route("/api/services", methods=["GET"])
def list_services():
    category = request.args.get("category")
    rows = get_all_services(category)
    return jsonify({"services": [serialize_service(r) for r in rows]}), 200


@service_bp.route("/api/services/<int:service_id>", methods=["GET"])
def get_service(service_id):
    service = get_service_by_id(service_id)
    if not service:
        return jsonify({"error": "Service not found."}), 404

    providers = get_providers_for_service(service_id)
    return jsonify({
        "service": serialize_service(service),
        "providers": [serialize_provider(p) for p in providers]
    }), 200
