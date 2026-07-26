from functools import wraps
from flask import request, jsonify, g
from app.models.session_model import get_user_by_token


def require_auth(f):
    """Decorator to enforce Bearer token authentication on Flask endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()

        if not token:
            return jsonify({"error": "Authorization token required."}), 401

        user = get_user_by_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired session session."}), 401

        g.current_user = user
        g.token = token
        return f(*args, **kwargs)
    return decorated
