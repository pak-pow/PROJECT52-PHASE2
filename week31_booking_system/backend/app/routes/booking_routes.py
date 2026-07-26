from flask import Blueprint, request, jsonify, g
from app.models.booking_model import (
    create_booking, get_user_bookings, get_booking_by_id, cancel_booking
)
from app.models.service_model import get_service_by_id
from app.models.provider_model import get_provider_by_id
from app.services.serializers import serialize_booking
from app.services.auth_service import require_auth

booking_bp = Blueprint("bookings", __name__)


@booking_bp.route("/api/bookings", methods=["POST"])
@require_auth
def create_new_booking():
    data = request.get_json(silent=True) or request.form
    provider_id = data.get("provider_id")
    service_id = data.get("service_id")
    booking_date = (data.get("booking_date") or "").strip()
    start_time = (data.get("start_time") or "").strip()
    end_time = (data.get("end_time") or "").strip()
    notes = (data.get("notes") or "").strip()

    if not provider_id or not service_id or not booking_date or not start_time or not end_time:
        return jsonify({"error": "Fields 'provider_id', 'service_id', 'booking_date', 'start_time', and 'end_time' are required."}), 400

    service = get_service_by_id(service_id)
    if not service:
        return jsonify({"error": "Specified service not found."}), 404

    provider = get_provider_by_id(provider_id)
    if not provider:
        return jsonify({"error": "Specified provider not found."}), 404

    try:
        booking_id = create_booking(
            g.current_user["id"], provider_id, service_id,
            booking_date, start_time, end_time, notes
        )
        row = get_booking_by_id(booking_id)
        return jsonify({"booking": serialize_booking(row)}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409


@booking_bp.route("/api/bookings/my-bookings", methods=["GET"])
@require_auth
def list_my_bookings():
    rows = get_user_bookings(g.current_user["id"])
    return jsonify({"bookings": [serialize_booking(r) for r in rows]}), 200


@booking_bp.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
@require_auth
def cancel_existing_booking(booking_id):
    try:
        success = cancel_booking(booking_id, g.current_user["id"])
        if not success:
            return jsonify({"error": "Booking not found."}), 404
        return jsonify({"message": "Booking cancelled successfully."}), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
