import pytest
from app.models.event_model import EventModel
from app.models.funnel_model import FunnelModel
from app.services.serializers import serialize_event, serialize_events_list

def test_health_check_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "week36_analytics_dashboard"
    assert "total_events_collected" in data

def test_create_event_model():
    evt = EventModel.create_event(
        event_name="pageview",
        session_id="sess_1001",
        url_path="/pricing",
        user_id="usr_55",
        referrer="https://google.com",
        device_type="desktop",
        browser="Chrome",
        os_name="Windows",
        country="United States",
        metadata={"plan": "pro"}
    )
    assert evt["id"] is not None
    assert evt["event_name"] == "pageview"
    assert evt["session_id"] == "sess_1001"
    assert evt["url_path"] == "/pricing"
    assert evt["device_type"] == "desktop"

def test_get_event_by_id():
    evt = EventModel.create_event(
        event_name="click",
        session_id="sess_1002",
        url_path="/features"
    )
    fetched = EventModel.get_by_id(evt["id"])
    assert fetched is not None
    assert fetched["event_name"] == "click"
    assert fetched["url_path"] == "/features"

def test_get_live_stream_events():
    for i in range(5):
        EventModel.create_event(
            event_name=f"event_{i}",
            session_id=f"sess_{i}",
            url_path=f"/path_{i}"
        )
    live = EventModel.get_live_stream(limit=3)
    assert len(live) == 3

def test_create_and_get_funnel_model():
    funnel = FunnelModel.create_funnel(
        name="Checkout Funnel",
        description="Checkout flow",
        steps=[
            {"step_name": "View Cart", "event_name": "view_cart"},
            {"step_name": "Enter Details", "event_name": "enter_details"},
            {"step_name": "Purchase", "event_name": "purchase"}
        ]
    )
    assert funnel["id"] is not None
    assert funnel["name"] == "Checkout Funnel"
    assert len(funnel["steps"]) == 3
    assert funnel["steps"][0]["step_name"] == "View Cart"
    assert funnel["steps"][2]["event_name"] == "purchase"

def test_serialize_event_with_metadata():
    evt = EventModel.create_event(
        event_name="signup",
        session_id="sess_1003",
        url_path="/signup",
        metadata={"referrer_campaign": "twitter_ad"}
    )
    serialized = serialize_event(evt)
    assert "metadata" in serialized
    assert serialized["metadata"]["referrer_campaign"] == "twitter_ad"
    assert "metadata_json" not in serialized
