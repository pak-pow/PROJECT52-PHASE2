from flask import Blueprint, request, jsonify
from app.models.provider_model import get_all_providers, get_provider_by_id
from app.services.availability_service import compute_available_slots
from app.services.serializers import serialize_provider

provider_bp = Blueprint("providers", __name__)


@provider_bp.route("/api/providers", methods=["GET"])
def list_providers():
    rows = get_all_providers()
    return jsonify({"providers": [serialize_provider(r) for r in rows]}), 200


@provider_bp.route("/api/providers/<int:provider_id>", methods=["GET"])
def get_provider(provider_id):
    provider = get_provider_by_id(provider_id)
    if not provider:
        return jsonify({"error": "Provider not found."}), 404
    return jsonify({"provider": serialize_provider(provider)}), 200


@provider_bp.route("/api/providers/<int:provider_id>/availability", methods=["GET"])
def check_availability(provider_id):
    service_id = request.args.get("service_id", type=int)
    date_str = request.args.get("date")

    if not service_id or not date_str:
        return jsonify({"error": "Query parameters 'service_id' and 'date' (YYYY-MM-DD) are required."}), 400

    provider = get_provider_by_id(provider_id)
    if not provider:
        return jsonify({"error": "Provider not found."}), 404

    slots = compute_available_slots(provider_id, service_id, date_str)
    return jsonify({
        "provider_id": provider_id,
        "service_id": service_id,
        "date": date_str,
        "slots": slots
    }), 200
