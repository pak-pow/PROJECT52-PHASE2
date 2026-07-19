from functools import wraps
from flask import request, jsonify, g
from app.models.session_model import get_user_by_token


def require_auth(f):
    """Route decorator: validates Bearer token, sets g.user. Returns 401 if invalid."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header."}), 401
        token = auth_header[7:].strip()
        user = get_user_by_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired token."}), 401
        g.user = user
        return f(*args, **kwargs)
    return decorated


def optional_auth(f):
    """Route decorator: validates Bearer token if present, sets g.user or None."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        g.user = None
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            g.user = get_user_by_token(token)
        return f(*args, **kwargs)
    return decorated
