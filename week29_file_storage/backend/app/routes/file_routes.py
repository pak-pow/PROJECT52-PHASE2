from flask import Blueprint, request, jsonify, send_file, g  # type: ignore
from app.services.auth_service import require_auth
from app.services.file_service import validate_file, generate_stored_name, serialize_file
from app.services.thumbnail_service import can_generate_thumbnail, generate_thumbnail, get_thumbnail_path, delete_thumbnail
from app.models.file_model import insert_file, get_all_files, get_file_by_id, delete_file_by_id, update_file_name
from app.storage.local import LocalStorage
from app.config.settings import Config

file_bp = Blueprint("files", __name__, url_prefix="/api/files")

storage = LocalStorage()


@file_bp.route("/upload", methods=["POST"])
@require_auth
def upload_files():
    """Upload one or more files (multipart/form-data)."""
    uploaded = request.files.getlist("files")
    if not uploaded:
        return jsonify({"error": "No files provided."}), 400

    if len(uploaded) > Config.MAX_FILES_PER_REQUEST:
        return jsonify({"error": f"Maximum {Config.MAX_FILES_PER_REQUEST} files per upload."}), 400

    results = []
    errors = []

    for f in uploaded:
        valid, err = validate_file(f)
        if not valid:
            errors.append({"file": f.filename, "error": err})
            continue

        stored_name = generate_stored_name(f.filename)
        category = Config.get_category(f.content_type or "")

        # Save file to disk
        dest = storage.save(f, stored_name)

        # Generate thumbnail for images
        has_thumb = False
        if can_generate_thumbnail(f.content_type or ""):
            has_thumb = generate_thumbnail(dest, stored_name)

        # Insert metadata into database
        file_id = insert_file(
            user_id=g.user["id"],
            original_name=f.filename,
            stored_name=stored_name,
            mime_type=f.content_type or "application/octet-stream",
            file_size=f.content_length or 0,
            category=category,
            has_thumbnail=has_thumb,
        )

        results.append({
            "id": file_id,
            "original_name": f.filename,
            "category": category,
            "has_thumbnail": has_thumb,
        })

    status = 201 if results else 400
    return jsonify({"uploaded": results, "errors": errors}), status


@file_bp.route("", methods=["GET"])
@require_auth
def list_files():
    """List all files for the authenticated user, optional ?category= filter."""
    category = request.args.get("category")
    rows = get_all_files(g.user["id"], category)
    return jsonify([serialize_file(r) for r in rows]), 200


@file_bp.route("/<int:file_id>", methods=["GET"])
@require_auth
def get_file(file_id):
    """Return metadata for a single file."""
    row = get_file_by_id(file_id, g.user["id"])
    if not row:
        return jsonify({"error": "File not found."}), 404
    return jsonify(serialize_file(row)), 200


@file_bp.route("/<int:file_id>/download", methods=["GET"])
@require_auth
def download_file(file_id):
    """Stream the actual file to the client."""
    row = get_file_by_id(file_id, g.user["id"])
    if not row:
        return jsonify({"error": "File not found."}), 404

    path = storage.get_path(row["stored_name"])
    if not path:
        return jsonify({"error": "File missing from storage."}), 500

    return send_file(
        path,
        mimetype=row["mime_type"],
        as_attachment=True,
        download_name=row["original_name"],
    )


@file_bp.route("/<int:file_id>/thumbnail", methods=["GET"])
@require_auth
def get_thumbnail(file_id):
    """Serve the thumbnail for an image file."""
    row = get_file_by_id(file_id, g.user["id"])
    if not row:
        return jsonify({"error": "File not found."}), 404

    if not row["has_thumbnail"]:
        return jsonify({"error": "No thumbnail available."}), 404

    path = get_thumbnail_path(row["stored_name"])
    if not path:
        return jsonify({"error": "Thumbnail missing from storage."}), 500

    return send_file(path, mimetype="image/jpeg")


@file_bp.route("/<int:file_id>", methods=["DELETE"])
@require_auth
def delete_file(file_id):
    """Delete a file + its thumbnail from disk and database."""
    info = delete_file_by_id(file_id, g.user["id"])
    if not info:
        return jsonify({"error": "File not found."}), 404

    # Clean up from disk
    storage.delete(info["stored_name"])
    if info["has_thumbnail"]:
        delete_thumbnail(info["stored_name"])

    return jsonify({"message": "File deleted."}), 200


@file_bp.route("/<int:file_id>", methods=["PUT"])
@require_auth
def rename_file(file_id):
    """Rename a file's original name."""
    data = request.get_json(silent=True)
    if not data or "original_name" not in data:
        return jsonify({"error": "Missing original_name parameter."}), 400

    new_name = data["original_name"].strip()
    if not new_name:
        return jsonify({"error": "Filename cannot be empty."}), 400

    row = get_file_by_id(file_id, g.user["id"])
    if not row:
        return jsonify({"error": "File not found."}), 404

    update_file_name(file_id, g.user["id"], new_name)
    return jsonify({"message": "File renamed successfully."}), 200
