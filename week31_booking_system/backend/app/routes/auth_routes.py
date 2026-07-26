from flask import Blueprint, request, jsonify, g
from app.models.user_model import create_user, verify_password, get_user_by_username
from app.models.session_model import create_session, delete_session
from app.services.serializers import serialize_user
from app.services.auth_service import require_auth

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or request.form
    username = (data.get("username") or "").strip()
    display_name = (data.get("display_name") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not username or not display_name or not email or not password:
        return jsonify({"error": "All fields (username, display_name, email, password) are required."}), 400

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    try:
        user_id = create_user(username, display_name, email, password)
        token = create_session(user_id)
        user = get_user_by_username(username)
        return jsonify({
            "token": token,
            "user": serialize_user(user)
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or request.form
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user = verify_password(username, password)
    if not user:
        return jsonify({"error": "Invalid username or password."}), 401

    token = create_session(user["id"])
    return jsonify({
        "token": token,
        "user": serialize_user(user)
    }), 200


@auth_bp.route("/api/auth/me", methods=["GET"])
@require_auth
def get_current_user_profile():
    return jsonify({"user": serialize_user(g.current_user)}), 200


@auth_bp.route("/api/auth/logout", methods=["POST"])
@require_auth
def logout():
    delete_session(g.token)
    return jsonify({"message": "Logged out successfully."}), 200
