from functools import wraps
from flask import request, jsonify, g  # type: ignore
from app.models.user_model import get_user_by_token


def require_auth(f):
    """
    Decorator that enforces token-based authentication.
    Reads the Bearer token from the Authorization header and
    attaches the user row to flask.g.user.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header."}), 401

        token = auth_header[7:]  # strip "Bearer "
        user = get_user_by_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired token."}), 401

        g.user = user
        return f(*args, **kwargs)

    return decorated
