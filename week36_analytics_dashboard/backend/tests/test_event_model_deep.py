import pytest
from app.models.event_model import EventModel
from app.services.serializers import serialize_event, serialize_events_list

def test_event_creation_default_fields():
    evt = EventModel.create_event(
        event_name="custom_event",
        session_id="def_sess_1",
        url_path="/landing"
    )
    assert evt["device_type"] == "desktop"
    assert evt["browser"] == "Chrome"
    assert evt["os"] == "Windows"
    assert evt["country"] == "United States"
    assert evt["user_id"] is None
    assert evt["referrer"] is None
    assert evt["metadata_json"] is None

def test_event_creation_with_complex_metadata():
    meta = {
        "cart_total": 99.95,
        "item_count": 3,
        "tags": ["promo", "summer_sale"],
        "nested": {"coupon": "SAVE20"}
    }
    evt = EventModel.create_event(
        event_name="purchase",
        session_id="meta_sess_1",
        url_path="/checkout",
        metadata=meta
    )
    serialized = serialize_event(evt)
    assert serialized["metadata"]["cart_total"] == 99.95
    assert serialized["metadata"]["nested"]["coupon"] == "SAVE20"

def test_event_creation_with_custom_timestamp():
    custom_time = "2026-05-10 14:30:00"
    evt = EventModel.create_event(
        event_name="historic_pageview",
        session_id="hist_sess_1",
        url_path="/archive",
        created_at=custom_time
    )
    assert evt["created_at"] == custom_time

def test_get_event_by_nonexistent_id():
    evt = EventModel.get_by_id(999999)
    assert evt is None

def test_get_total_count_increments_correctly():
    init_count = EventModel.get_total_count()
    EventModel.create_event("inc_test", "inc_s_1", "/test1")
    EventModel.create_event("inc_test", "inc_s_2", "/test2")
    assert EventModel.get_total_count() == init_count + 2

def test_get_live_stream_ordering():
    # Insert 3 events
    e1 = EventModel.create_event("stream_1", "st_1", "/1")
    e2 = EventModel.create_event("stream_2", "st_2", "/2")
    e3 = EventModel.create_event("stream_3", "st_3", "/3")

    stream = EventModel.get_live_stream(limit=3)
    ids = [e["id"] for e in stream]
    assert ids[0] == e3["id"] # Most recent first
    assert ids[1] == e2["id"]
    assert ids[2] == e1["id"]

def test_live_stream_default_limit():
    for i in range(10):
        EventModel.create_event(f"bulk_{i}", f"sess_{i}", f"/bulk_{i}")
    stream = EventModel.get_live_stream(limit=5)
    assert len(stream) == 5

def test_serializer_empty_input():
    assert serialize_event(None) == {}
    assert serialize_events_list([]) == []
    assert serialize_events_list(None) == []

def test_serializer_invalid_metadata_json():
    # Simulate bad json string in database
    bad_evt = {"id": 1, "metadata_json": "INVALID_JSON_STRING"}
    res = serialize_event(bad_evt)
    assert res["metadata"] == {}

def test_serialize_events_list():
    evt1 = EventModel.create_event("ev1", "s1", "/1", metadata={"a": 1})
    evt2 = EventModel.create_event("ev2", "s2", "/2", metadata={"b": 2})
    
    serialized_list = serialize_events_list([evt1, evt2])
    assert len(serialized_list) == 2
    assert serialized_list[0]["metadata"]["a"] == 1
    assert serialized_list[1]["metadata"]["b"] == 2

def test_event_with_unicode_characters():
    evt = EventModel.create_event(
        event_name="view_日本語",
        session_id="sess_unicode",
        url_path="/page/café-résumé",
        country="Deutschland 🇩🇪"
    )
    assert evt["event_name"] == "view_日本語"
    assert evt["url_path"] == "/page/café-résumé"
    assert evt["country"] == "Deutschland 🇩🇪"

def test_event_with_long_url_and_query_params():
    long_url = "/search?q=machine+learning+and+analytics+in+python&category=tech&page=1&sort=desc&filter=active"
    evt = EventModel.create_event("search_query", "sess_long", long_url)
    assert evt["url_path"] == long_url

def test_event_multiple_events_same_session():
    for i in range(4):
        EventModel.create_event("pageview", "shared_session_xyz", f"/step_{i}")
    live = EventModel.get_live_stream(limit=10)
    matching = [e for e in live if e["session_id"] == "shared_session_xyz"]
    assert len(matching) == 4

def test_event_model_authenticated_vs_anonymous():
    anon = EventModel.create_event("view", "anon_s", "/home", user_id=None)
    auth = EventModel.create_event("view", "auth_s", "/home", user_id="user_admin_99")
    assert anon["user_id"] is None
    assert auth["user_id"] == "user_admin_99"

def test_event_model_all_device_types():
    d1 = EventModel.create_event("v", "s1", "/", device_type="desktop")
    d2 = EventModel.create_event("v", "s2", "/", device_type="mobile")
    d3 = EventModel.create_event("v", "s3", "/", device_type="tablet")
    assert d1["device_type"] == "desktop"
    assert d2["device_type"] == "mobile"
    assert d3["device_type"] == "tablet"
