import secrets
from flask import Blueprint, request, jsonify, current_app #type: ignore
from app.db import get_db
from app.middlewares.admin_middleware import admin_required

admin_bp = Blueprint("admin", __name__)


# ── Auth ──────────────────────────────────────────────────────────────────────

@admin_bp.route("/admin/login", methods=["POST"])
def admin_login():
    """
    POST /api/admin/login
    Validate admin credentials and issue a session token.

    Body (JSON):
        username (str)
        password (str)

    Returns:
        200 { token: "..." }
        401 { error: "..." }
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    expected_user = current_app.config["ADMIN_USERNAME"]
    expected_pass = current_app.config["ADMIN_PASSWORD"]

    if username != expected_user or password != expected_pass:
        return jsonify({"error": "Invalid credentials"}), 401

    token = secrets.token_hex(32)
    db = get_db()
    db.execute("INSERT INTO admin_sessions (token) VALUES (?)", (token,))
    db.commit()

    return jsonify({"token": token}), 200


@admin_bp.route("/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    """
    POST /api/admin/logout  [Admin only]
    Revoke the current session token.
    """
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(" ", 1)[1].strip()

    db = get_db()
    db.execute("DELETE FROM admin_sessions WHERE token = ?", (token,))
    db.commit()

    return jsonify({"message": "Logged out successfully"}), 200


# ── Messages ──────────────────────────────────────────────────────────────────

@admin_bp.route("/admin/messages", methods=["GET"])
@admin_required
def list_messages():
    """
    GET /api/admin/messages  [Admin only]
    Return all contact messages ordered by newest first.
    """
    db = get_db()
    rows = db.execute(
        "SELECT * FROM contact_messages ORDER BY created_at DESC"
    ).fetchall()

    messages = [
        {
            "id":         row["id"],
            "name":       row["name"],
            "email":      row["email"],
            "subject":    row["subject"],
            "message":    row["message"],
            "is_read":    bool(row["is_read"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
    return jsonify(messages), 200


@admin_bp.route("/admin/messages/<int:message_id>/read", methods=["PATCH"])
@admin_required
def toggle_read(message_id):
    """
    PATCH /api/admin/messages/<id>/read  [Admin only]
    Toggle the is_read flag on a message.
    """
    db = get_db()
    row = db.execute(
        "SELECT id, is_read FROM contact_messages WHERE id = ?", (message_id,)
    ).fetchone()

    if row is None:
        return jsonify({"error": "Message not found"}), 404

    new_state = 0 if row["is_read"] else 1
    db.execute(
        "UPDATE contact_messages SET is_read = ? WHERE id = ?",
        (new_state, message_id),
    )
    db.commit()

    return jsonify({"id": message_id, "is_read": bool(new_state)}), 200


@admin_bp.route("/admin/messages/<int:message_id>", methods=["DELETE"])
@admin_required
def delete_message(message_id):
    """
    DELETE /api/admin/messages/<id>  [Admin only]
    Permanently delete a contact message.
    """
    db = get_db()
    row = db.execute(
        "SELECT id FROM contact_messages WHERE id = ?", (message_id,)
    ).fetchone()

    if row is None:
        return jsonify({"error": "Message not found"}), 404

    db.execute("DELETE FROM contact_messages WHERE id = ?", (message_id,))
    db.commit()
    return "", 204
