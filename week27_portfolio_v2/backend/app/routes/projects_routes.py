from flask import Blueprint, request, jsonify #type: ignore
from app.db import get_db
from app.middlewares.admin_middleware import admin_required

projects_bp = Blueprint("projects", __name__)


def _project_to_dict(row):
    """Convert a sqlite3.Row to a plain dict."""
    return {
        "id":          row["id"],
        "title":       row["title"],
        "description": row["description"],
        "tech_stack":  row["tech_stack"],
        "github_url":  row["github_url"],
        "live_url":    row["live_url"],
        "status":      row["status"],
        "sort_order":  row["sort_order"],
        "featured":    row["featured"],
        "created_at":  row["created_at"],
    }


@projects_bp.route("/projects", methods=["GET"])
def list_projects():
    """
    GET /api/projects
    Public — list all projects ordered by sort_order.
    """
    db = get_db()
    rows = db.execute(
        "SELECT * FROM projects ORDER BY sort_order ASC, id ASC"
    ).fetchall()
    return jsonify([_project_to_dict(r) for r in rows]), 200


@projects_bp.route("/projects", methods=["POST"])
@admin_required
def create_project():
    """
    POST /api/projects  [Admin only]
    Add a new project.
    """
    data = request.get_json(silent=True) or {}

    required = ["title", "description", "tech_stack"]
    for field in required:
        if not data.get(field, "").strip():
            return jsonify({"error": f"'{field}' is required"}), 400

    db = get_db()
    cursor = db.execute(
        """INSERT INTO projects (title, description, tech_stack, github_url, live_url, status, sort_order, featured)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["title"].strip(),
            data["description"].strip(),
            data["tech_stack"].strip(),
            data.get("github_url", "").strip() or None,
            data.get("live_url", "").strip() or None,
            data.get("status", "In Progress").strip(),
            int(data.get("sort_order", 0)),
            1 if data.get("featured") else 0,
        ),
    )
    db.commit()

    new_row = db.execute(
        "SELECT * FROM projects WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    return jsonify(_project_to_dict(new_row)), 201


@projects_bp.route("/projects/<int:project_id>", methods=["PUT"])
@admin_required
def update_project(project_id):
    """
    PUT /api/projects/<id>  [Admin only]
    Update an existing project.
    """
    db = get_db()
    existing = db.execute(
        "SELECT * FROM projects WHERE id = ?", (project_id,)
    ).fetchone()

    if existing is None:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json(silent=True) or {}

    db.execute(
        """UPDATE projects
           SET title = ?, description = ?, tech_stack = ?,
               github_url = ?, live_url = ?, status = ?, sort_order = ?, featured = ?
           WHERE id = ?""",
        (
            data.get("title", existing["title"]).strip(),
            data.get("description", existing["description"]).strip(),
            data.get("tech_stack", existing["tech_stack"]).strip(),
            data.get("github_url", existing["github_url"]),
            data.get("live_url", existing["live_url"]),
            data.get("status", existing["status"]).strip(),
            int(data.get("sort_order", existing["sort_order"])),
            1 if data.get("featured", existing["featured"]) else 0,
            project_id,
        ),
    )
    db.commit()

    updated = db.execute(
        "SELECT * FROM projects WHERE id = ?", (project_id,)
    ).fetchone()
    return jsonify(_project_to_dict(updated)), 200


@projects_bp.route("/projects/<int:project_id>", methods=["DELETE"])
@admin_required
def delete_project(project_id):
    """
    DELETE /api/projects/<id>  [Admin only]
    Delete a project.
    """
    db = get_db()
    existing = db.execute(
        "SELECT id FROM projects WHERE id = ?", (project_id,)
    ).fetchone()

    if existing is None:
        return jsonify({"error": "Project not found"}), 404

    db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    db.commit()
    return "", 204
