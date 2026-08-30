from flask import Blueprint, jsonify
from app.models.event_model import EventModel

health_bp = Blueprint("health_bp", __name__)

@health_bp.route("/api/health", methods=["GET"])
def health_check():
    total_events = EventModel.get_total_count()
    return jsonify({
        "status": "ok",
        "service": "week36_analytics_dashboard",
        "message": "Analytics & Metrics Engine operational.",
        "total_events_collected": total_events
    }), 200
