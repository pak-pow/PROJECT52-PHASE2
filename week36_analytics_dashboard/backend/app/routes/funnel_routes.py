from flask import Blueprint, request, jsonify
from app.models.funnel_model import FunnelModel
from app.services.funnel_service import FunnelService

funnel_bp = Blueprint("funnel_bp", __name__)

@funnel_bp.route("/api/funnels", methods=["GET"])
def list_funnels():
    funnels = FunnelModel.get_all()
    return jsonify({
        "count": len(funnels),
        "funnels": funnels
    }), 200

@funnel_bp.route("/api/funnels/<int:funnel_id>", methods=["GET"])
def get_funnel_details(funnel_id):
    funnel = FunnelModel.get_by_id(funnel_id)
    if not funnel:
        return jsonify({"error": f"Funnel with ID {funnel_id} not found."}), 404
    return jsonify(funnel), 200

@funnel_bp.route("/api/funnels/<int:funnel_id>/metrics", methods=["GET"])
def get_funnel_metrics(funnel_id):
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    metrics = FunnelService.calculate_funnel_metrics(
        funnel_id=funnel_id,
        start_date=start_date,
        end_date=end_date
    )
    if not metrics:
        return jsonify({"error": f"Funnel with ID {funnel_id} not found."}), 404

    return jsonify(metrics), 200

@funnel_bp.route("/api/funnels", methods=["POST"])
def create_funnel():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    description = data.get("description")
    steps = data.get("steps", [])

    if not name or not isinstance(name, str) or name.strip() == "":
        return jsonify({"error": "Field 'name' is required."}), 400

    if not isinstance(steps, list) or len(steps) == 0:
        return jsonify({"error": "Funnel must contain at least one step in 'steps' array."}), 400

    # Validate each step has step_name and event_name
    for s in steps:
        if not s.get("step_name") or not s.get("event_name"):
            return jsonify({"error": "Each step must contain 'step_name' and 'event_name'."}), 400

    try:
        created = FunnelModel.create_funnel(name=name.strip(), description=description, steps=steps)
        return jsonify({
            "message": "Funnel created successfully.",
            "funnel": created
        }), 201
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return jsonify({"error": f"A funnel named '{name}' already exists."}), 409
        return jsonify({"error": f"Failed to create funnel: {str(e)}"}), 500
