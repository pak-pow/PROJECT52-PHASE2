from flask import Blueprint, request, jsonify  # type: ignore
from app.models.user_model import create_user, authenticate_user, create_session, delete_session

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user. Expects JSON {username, password}."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    try:
        user_id = create_user(username, password)
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

    token = create_session(user_id)
    return jsonify({"user_id": user_id, "username": username, "token": token}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Log in with credentials. Expects JSON {username, password}."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = authenticate_user(username, password)
    if not user:
        return jsonify({"error": "Invalid username or password."}), 401

    token = create_session(user["id"])
    return jsonify({
        "user_id": user["id"],
        "username": user["username"],
        "token": token,
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Log out by invalidating the session token."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token."}), 400

    token = auth_header[7:]
    delete_session(token)
    return jsonify({"message": "Logged out."}), 200
