from flask import Blueprint, request, jsonify #type: ignore
from app.services.auth_service import AuthService
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity #type: ignore

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing username or password"}), 400

    try:
        user_id = AuthService.register_user(data['username'], data['password'])
        if user_id:
            return jsonify({"message": "User created successfully!"}), 201
        return jsonify({"error": "Username already exists"}), 409
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing username or password"}), 400

    token = AuthService.login_user(data['username'], data['password'])

    if token:
        return jsonify({"message": "Login successful", "access_token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """Returns the currently authenticated user's profile. Used by the frontend to display 'Welcome, [User]'."""
    user_id = get_jwt_identity()
    user = User.get_by_id(user_id)
    if user:
        return jsonify({
            "id": user['id'],
            "username": user['username'],
            "created_at": user['created_at']
        }), 200
    return jsonify({"error": "User not found"}), 404