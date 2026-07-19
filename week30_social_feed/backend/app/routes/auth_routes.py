from flask import Blueprint, request, jsonify, g
from app.models.user_model import create_user, verify_password
from app.models.session_model import create_session, delete_session
from app.services.auth_service import require_auth
from app.config.settings import Config

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """POST /api/auth/register — create a new account and return a session token."""
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    display_name = str(data.get("display_name", "")).strip() or username
    password = str(data.get("password", ""))

    # ── Validate username ──────────────────────────────────────
    if len(username) < Config.MIN_USERNAME_LEN or len(username) > Config.MAX_USERNAME_LEN:
        return jsonify({"error": f"Username must be {Config.MIN_USERNAME_LEN}–{Config.MAX_USERNAME_LEN} characters."}), 400
    if not username.replace("_", "").isalnum():
        return jsonify({"error": "Username may only contain letters, numbers, and underscores."}), 400

    # ── Validate display name ──────────────────────────────────
    if len(display_name) > Config.MAX_DISPLAY_NAME_LEN:
        return jsonify({"error": f"Display name cannot exceed {Config.MAX_DISPLAY_NAME_LEN} characters."}), 400

    # ── Validate password ──────────────────────────────────────
    if len(password) < Config.MIN_PASSWORD_LEN:
        return jsonify({"error": f"Password must be at least {Config.MIN_PASSWORD_LEN} characters."}), 400

    try:
        user_id = create_user(username, display_name, password)
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

    token = create_session(user_id)
    return jsonify({"token": token, "username": username, "display_name": display_name}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """POST /api/auth/login — validate credentials and return a session token."""
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user = verify_password(username, password)
    if not user:
        return jsonify({"error": "Invalid username or password."}), 401

    token = create_session(user["id"])
    return jsonify({
        "token": token,
        "username": user["username"],
        "display_name": user["display_name"],
        "avatar_path": user["avatar_path"],
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    """POST /api/auth/logout — invalidate the current session token."""
    token = request.headers.get("Authorization", "")[7:].strip()
    delete_session(token)
    return jsonify({"message": "Logged out successfully."}), 200


@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    """GET /api/auth/me — return current authenticated user details."""
    return jsonify({
        "id": g.user["id"],
        "username": g.user["username"],
        "display_name": g.user["display_name"],
        "avatar_path": g.user["avatar_path"],
        "bio": g.user["bio"],
    }), 200
