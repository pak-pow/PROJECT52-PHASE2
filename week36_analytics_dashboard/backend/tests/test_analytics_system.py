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

# ══════════════════════════════════════════════════════════════
# Day 2 Tests: Parsers, Aggregation Engine & Funnel Service
# ══════════════════════════════════════════════════════════════

from app.services.ua_parser import UserAgentParser
from app.services.aggregation_service import AggregationService
from app.services.funnel_service import FunnelService

def test_ua_parser_desktop_chrome():
    ua_str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    parsed = UserAgentParser.parse_user_agent(ua_str)
    assert parsed["device_type"] == "desktop"
    assert parsed["browser"] == "Chrome"
    assert parsed["os"] == "Windows"

def test_ua_parser_mobile_iphone_safari():
    ua_str = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
    parsed = UserAgentParser.parse_user_agent(ua_str)
    assert parsed["device_type"] == "mobile"
    assert parsed["browser"] == "Safari"
    assert parsed["os"] == "iOS"

def test_ua_parser_tablet_ipad():
    ua_str = "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    parsed = UserAgentParser.parse_user_agent(ua_str)
    assert parsed["device_type"] == "tablet"
    assert parsed["browser"] == "Safari"
    assert parsed["os"] == "iOS"

def test_ua_parser_empty_fallback():
    parsed = UserAgentParser.parse_user_agent("")
    assert parsed["device_type"] == "desktop"
    assert parsed["browser"] == "Other"
    assert parsed["os"] == "Other"

def test_referrer_categorizer():
    assert UserAgentParser.categorize_referrer("https://www.google.com/search?q=analytics") == "Search Engines"
    assert UserAgentParser.categorize_referrer("https://t.co/xyz123") == "Social Media"
    assert UserAgentParser.categorize_referrer("https://github.com/pak-pow") == "Developer / Tech"
    assert UserAgentParser.categorize_referrer(None) == "Direct"
    assert UserAgentParser.categorize_referrer("") == "Direct"

def test_aggregation_service_overview():
    # Insert test events
    EventModel.create_event("pageview", "sess_agg_1", "/home")
    EventModel.create_event("pageview", "sess_agg_1", "/pricing")
    EventModel.create_event("click", "sess_agg_1", "/pricing")
    EventModel.create_event("pageview", "sess_agg_2", "/home") # Single event session (bounced)

    overview = AggregationService.get_overview_metrics()
    assert overview["pageviews"] >= 3
    assert overview["unique_visitors"] >= 2
    assert "bounce_rate_pct" in overview
    assert "avg_views_per_session" in overview

def test_aggregation_service_timeseries_daily():
    EventModel.create_event("pageview", "sess_ts_1", "/dashboard", created_at="2026-08-01 10:00:00")
    EventModel.create_event("pageview", "sess_ts_2", "/dashboard", created_at="2026-08-01 12:00:00")
    EventModel.create_event("pageview", "sess_ts_3", "/dashboard", created_at="2026-08-02 09:00:00")

    ts = AggregationService.get_timeseries_traffic(start_date="2026-08-01", end_date="2026-08-02", interval="day")
    assert len(ts) == 2
    assert ts[0]["bucket"] == "2026-08-01"
    assert ts[0]["pageviews"] == 2
    assert ts[1]["bucket"] == "2026-08-02"
    assert ts[1]["pageviews"] == 1

def test_aggregation_service_breakdowns():
    EventModel.create_event("pageview", "sess_bd_1", "/app", device_type="mobile", browser="Safari", os_name="iOS", country="Canada")
    EventModel.create_event("pageview", "sess_bd_2", "/app", device_type="desktop", browser="Chrome", os_name="Windows", country="United States")

    breakdowns = AggregationService.get_breakdowns()
    assert "devices" in breakdowns
    assert "browsers" in breakdowns
    assert "operating_systems" in breakdowns
    assert "countries" in breakdowns

def test_aggregation_service_top_pages():
    EventModel.create_event("pageview", "sess_top_1", "/features")
    EventModel.create_event("pageview", "sess_top_2", "/features")
    EventModel.create_event("pageview", "sess_top_3", "/pricing")

    top_pages = AggregationService.get_top_pages(limit=5)
    assert len(top_pages) >= 2
    assert top_pages[0]["url_path"] == "/features"
    assert top_pages[0]["views"] >= 2

def test_funnel_service_multi_step_calculation():
    # Create test funnel
    f = FunnelModel.create_funnel(
        name="Test Signup Funnel",
        steps=[
            {"step_name": "Step 1", "event_name": "view_landing"},
            {"step_name": "Step 2", "event_name": "click_cta"},
            {"step_name": "Step 3", "event_name": "complete_signup"}
        ]
    )

    # User 1 completes all 3 steps
    EventModel.create_event("view_landing", "sess_fn_1", "/")
    EventModel.create_event("click_cta", "sess_fn_1", "/")
    EventModel.create_event("complete_signup", "sess_fn_1", "/signup")

    # User 2 completes step 1 and 2, drops off before 3
    EventModel.create_event("view_landing", "sess_fn_2", "/")
    EventModel.create_event("click_cta", "sess_fn_2", "/")

    # User 3 completes step 1 only
    EventModel.create_event("view_landing", "sess_fn_3", "/")

    metrics = FunnelService.calculate_funnel_metrics(f["id"])
    assert metrics is not None
    assert metrics["initial_visitors"] == 3
    assert metrics["final_conversions"] == 1
    assert metrics["overall_conversion_pct"] == 33.33
    assert len(metrics["steps_analysis"]) == 3
    assert metrics["steps_analysis"][0]["visitors_reached"] == 3
    assert metrics["steps_analysis"][1]["visitors_reached"] == 2
    assert metrics["steps_analysis"][2]["visitors_reached"] == 1
