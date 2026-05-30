from flask import Blueprint, request, jsonify #type: ignore
from flask_jwt_extended import create_access_token #type: ignore
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing username or password"}), 400

    user = User.verify_password(data['username'], data['password'])
    
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user['id']))
    
    return jsonify({
        "message": "Login successful!",
        "token": access_token
    }), 200