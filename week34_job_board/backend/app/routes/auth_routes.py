from flask import Blueprint, request, jsonify
from app.models.user_model import UserModel

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    role = data.get("role", "applicant").strip().lower()
    company_name = data.get("company_name", "").strip()

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required."}), 400

    if role not in ["applicant", "employer"]:
        return jsonify({"error": "Role must be 'applicant' or 'employer'."}), 400

    existing = UserModel.get_by_email(email)
    if existing:
        return jsonify({"error": "An account with this email already exists."}), 409

    try:
        user = UserModel.create_user(username, email, password, role, company_name)
        return jsonify({
            "message": "User registered successfully.",
            "user": user
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = UserModel.verify_password(email, password)
    if not user:
        return jsonify({"error": "Invalid email or password."}), 401

    return jsonify({
        "message": "Login successful.",
        "user": user
    }), 200
