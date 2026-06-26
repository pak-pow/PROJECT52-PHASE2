from flask import Blueprint, request, jsonify #type: ignore
from app.db import get_db

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact", methods=["POST"])
def submit_contact():
    """
    POST /api/contact
    Save a visitor contact message to the database.

    Body (JSON):
        name    (str, required)
        email   (str, required)
        subject (str, required)
        message (str, required)

    Returns:
        201 { message: "Message sent!" }
        400 { error: "..." }  — validation failure
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # --- Validation ---
    required = ["name", "email", "subject", "message"]
    for field in required:
        if not data.get(field, "").strip():
            return jsonify({"error": f"'{field}' is required"}), 400

    # Basic email format check
    email = data["email"].strip()
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"error": "A valid email address is required"}), 400

    db = get_db()
    db.execute(
        """INSERT INTO contact_messages (name, email, subject, message)
           VALUES (?, ?, ?, ?)""",
        (
            data["name"].strip(),
            email,
            data["subject"].strip(),
            data["message"].strip(),
        ),
    )
    db.commit()

    return jsonify({"message": "Message sent! I'll get back to you soon."}), 201
