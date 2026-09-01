from flask import Blueprint, request, jsonify
from app.models.event_model import EventModel
from app.services.ua_parser import UserAgentParser
from app.services.serializers import serialize_event, serialize_events_list

event_bp = Blueprint("event_bp", __name__)

@event_bp.route("/api/events", methods=["POST"])
def track_event():
    data = request.get_json(silent=True) or {}
    
    event_name = data.get("event_name")
    session_id = data.get("session_id")
    url_path = data.get("url_path", "/")

    if not event_name or not session_id:
        return jsonify({"error": "Fields 'event_name' and 'session_id' are required."}), 400

    user_id = data.get("user_id")
    referrer = data.get("referrer")
    country = data.get("country", "United States")
    metadata = data.get("metadata")

    # Extract & Parse User-Agent Header if not explicitly provided
    ua_header = request.headers.get("User-Agent", "")
    parsed_ua = UserAgentParser.parse_user_agent(ua_header)

    device_type = data.get("device_type") or parsed_ua.get("device_type", "desktop")
    browser = data.get("browser") or parsed_ua.get("browser", "Chrome")
    os_name = data.get("os") or parsed_ua.get("os", "Windows")

    created_event = EventModel.create_event(
        event_name=event_name,
        session_id=session_id,
        url_path=url_path,
        user_id=user_id,
        referrer=referrer,
        device_type=device_type,
        browser=browser,
        os_name=os_name,
        country=country,
        metadata=metadata
    )

    return jsonify({
        "message": "Event recorded successfully.",
        "event": serialize_event(created_event)
    }), 201

@event_bp.route("/api/events/batch", methods=["POST"])
def track_events_batch():
    data = request.get_json(silent=True) or {}
    events = data.get("events", [])

    if not isinstance(events, list) or len(events) == 0:
        return jsonify({"error": "Payload must contain a non-empty 'events' list."}), 400

    ua_header = request.headers.get("User-Agent", "")
    parsed_ua = UserAgentParser.parse_user_agent(ua_header)

    created_list = []
    for evt in events:
        event_name = evt.get("event_name")
        session_id = evt.get("session_id")
        url_path = evt.get("url_path", "/")

        if not event_name or not session_id:
            continue

        created = EventModel.create_event(
            event_name=event_name,
            session_id=session_id,
            url_path=url_path,
            user_id=evt.get("user_id"),
            referrer=evt.get("referrer"),
            device_type=evt.get("device_type") or parsed_ua.get("device_type", "desktop"),
            browser=evt.get("browser") or parsed_ua.get("browser", "Chrome"),
            os_name=evt.get("os") or parsed_ua.get("os", "Windows"),
            country=evt.get("country", "United States"),
            metadata=evt.get("metadata")
        )
        created_list.append(created)

    return jsonify({
        "message": f"Successfully ingested {len(created_list)} events in batch.",
        "count": len(created_list),
        "events": serialize_events_list(created_list)
    }), 201

@event_bp.route("/api/events/live", methods=["GET"])
def get_live_stream():
    limit = request.args.get("limit", default=50, type=int)
    limit = min(max(limit, 1), 200) # Clamp between 1 and 200
    
    events = EventModel.get_live_stream(limit=limit)
    return jsonify({
        "limit": limit,
        "count": len(events),
        "events": serialize_events_list(events)
    }), 200
