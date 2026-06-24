from functools import wraps
from flask import request, jsonify, g #type: ignore
from app.models import user_model

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        token = auth_header.split(' ')[1]
        user = user_model.get_user_by_session_token(token)
        if not user:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        g.user = user
        return f(*args, **kwargs)
    return decorated_function
