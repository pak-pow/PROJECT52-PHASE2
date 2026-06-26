from functools import wraps
from flask import request, jsonify, g #type: ignore
from app.db import get_db


def admin_required(f):
    """
    Decorator that protects admin-only routes.

    Reads the Authorization header:
        Authorization: Bearer <token>

    If the token exists in admin_sessions, sets g.admin = True and proceeds.
    Otherwise returns 401 Unauthorized.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization header missing or malformed"}), 401

        token = auth_header.split(" ", 1)[1].strip()

        db = get_db()
        session = db.execute(
            "SELECT token FROM admin_sessions WHERE token = ?", (token,)
        ).fetchone()

        if session is None:
            return jsonify({"error": "Invalid or expired session token"}), 401

        g.admin = True
        return f(*args, **kwargs)

    return decorated_function
