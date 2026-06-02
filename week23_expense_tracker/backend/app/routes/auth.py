from flask import Blueprint, request, jsonify #type: ignore
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing username or password"}), 400
    
    token = AuthService.login_user(data['username'], data['password'])
    
    if token:
        return jsonify({"message": "Login Successful", "access_token": token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401