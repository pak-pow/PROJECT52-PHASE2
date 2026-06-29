from functools import wraps
from datetime import datetime
from flask import request, jsonify, g #type: ignore
from app.db import get_db


def admin_required(f):
    """
    Decorator that protects admin-only routes.

    Reads the Authorization header:
        Authorization: Bearer <token>

    If the token exists in admin_sessions and has not expired, sets g.admin = True and proceeds.
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
            "SELECT token, expires_at FROM admin_sessions WHERE token = ?", (token,)
        ).fetchone()

        if session is None:
            return jsonify({"error": "Invalid or expired session token"}), 401

        expires_at_val = session["expires_at"]
        if not expires_at_val:
            return jsonify({"error": "Invalid or expired session token"}), 401

        if isinstance(expires_at_val, str):
            try:
                # Normalize space to T for fromisoformat compatibility
                normalized = expires_at_val.replace(" ", "T")
                expires_at = datetime.fromisoformat(normalized)
            except ValueError:
                return jsonify({"error": "Invalid or expired session token"}), 401
        elif isinstance(expires_at_val, datetime):
            expires_at = expires_at_val
        else:
            return jsonify({"error": "Invalid or expired session token"}), 401

        if expires_at < datetime.utcnow():
            # Purge expired session token from DB
            db.execute("DELETE FROM admin_sessions WHERE token = ?", (token,))
            db.commit()
            return jsonify({"error": "Session expired"}), 401

        g.admin = True
        return f(*args, **kwargs)

    return decorated_function
