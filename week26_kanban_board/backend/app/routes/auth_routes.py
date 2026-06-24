from flask import Blueprint, request, jsonify, g #type: ignore
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import user_model

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400

    existing_user = user_model.get_user_by_username(username)
    if existing_user:
        return jsonify({'error': 'Username is already taken'}), 400

    try:
        password_hash = generate_password_hash(password)
        user_id = user_model.create_user(username, password_hash)
        
        # Auto-login on successful registration
        token = user_model.create_session(user_id)
        user = user_model.get_user_by_id(user_id)
        return jsonify({'token': token, 'user': user}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = user_model.get_user_by_username(username)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid username or password'}), 401

    token = user_model.create_session(user['id'])
    user_info = {'id': user['id'], 'username': user['username'], 'created_at': user['created_at']}
    return jsonify({'token': token, 'user': user_info}), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        user_model.delete_session(token)
    return '', 204

@auth_bp.route('/me', methods=['GET'])
def me():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    user = user_model.get_user_by_session_token(token)
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    return jsonify({'user': user}), 200
