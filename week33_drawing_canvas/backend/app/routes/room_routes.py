from flask import Blueprint, request, jsonify
from app.services.room_manager import room_manager

room_bp = Blueprint("room", __name__)

@room_bp.route("/api/rooms", methods=["POST"])
def create_room():
    data = request.get_json(silent=True) or {}
    custom_code = data.get("room_code")
    room_code = room_manager.create_room(custom_code)
    return jsonify({
        "room_code": room_code,
        "message": f"Room {room_code} created successfully."
    }), 201

@room_bp.route("/api/rooms/<room_code>", methods=["GET"])
def get_room(room_code):
    details = room_manager.get_room_details(room_code)
    if not details:
        return jsonify({"error": f"Room '{room_code}' not found."}), 404
    return jsonify(details), 200
