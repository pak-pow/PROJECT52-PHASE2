import uuid
import os
from app.config.settings import Config


def validate_file(file_obj):
    """
    Validate an uploaded file object.
    Returns (True, None) on success, (False, error_message) on failure.
    """
    if not file_obj or file_obj.filename == "":
        return False, "No file selected."

    mime = file_obj.content_type or ""
    if mime not in Config.ALLOWED_MIME_TYPES:
        return False, f"File type '{mime}' is not allowed."

    return True, None


def generate_stored_name(original_name):
    """Generate a UUID-based filename preserving the original extension."""
    _, ext = os.path.splitext(original_name)
    return f"{uuid.uuid4().hex}{ext.lower()}"


def serialize_file(row):
    """Convert a file DB row to a public dict."""
    uploaded_at = row["uploaded_at"]
    if uploaded_at and "T" not in uploaded_at:
        uploaded_at = f"{uploaded_at.replace(' ', 'T')}Z"
    return {
        "id": row["id"],
        "original_name": row["original_name"],
        "mime_type": row["mime_type"],
        "file_size": row["file_size"],
        "category": row["category"],
        "has_thumbnail": bool(row["has_thumbnail"]),
        "uploaded_at": uploaded_at,
    }
