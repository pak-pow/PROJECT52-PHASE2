import pytest
from app.models.event_model import EventModel
from app.services.aggregation_service import AggregationService

def test_aggregation_empty_database():
    overview = AggregationService.get_overview_metrics()
    assert overview["total_events"] == 0
    assert overview["pageviews"] == 0
    assert overview["unique_visitors"] == 0
    assert overview["bounce_rate_pct"] == 0.0
    assert overview["avg_views_per_session"] == 0.0

def test_aggregation_bounce_rate_100_percent():
    # 3 sessions, each with only 1 event -> 100% bounce rate
    EventModel.create_event("pageview", "b_sess_1", "/landing")
    EventModel.create_event("pageview", "b_sess_2", "/landing")
    EventModel.create_event("pageview", "b_sess_3", "/landing")

    overview = AggregationService.get_overview_metrics()
    assert overview["bounce_rate_pct"] == 100.0
    assert overview["unique_visitors"] == 3

def test_aggregation_bounce_rate_zero_percent():
    # 2 sessions, each with 2 pageviews -> 0% bounce rate
    EventModel.create_event("pageview", "nb_sess_1", "/page1")
    EventModel.create_event("pageview", "nb_sess_1", "/page2")
    EventModel.create_event("pageview", "nb_sess_2", "/page1")
    EventModel.create_event("pageview", "nb_sess_2", "/page2")

    overview = AggregationService.get_overview_metrics()
    assert overview["bounce_rate_pct"] == 0.0
    assert overview["unique_visitors"] == 2
    assert overview["avg_views_per_session"] == 2.0

def test_aggregation_bounce_rate_half():
    # 1 single-event session, 1 multi-event session -> 50% bounce rate
    EventModel.create_event("pageview", "half_1", "/page1")
    EventModel.create_event("pageview", "half_2", "/page1")
    EventModel.create_event("click", "half_2", "/page2")

    overview = AggregationService.get_overview_metrics()
    assert overview["bounce_rate_pct"] == 50.0

def test_aggregation_avg_pageviews_calculation():
    # 1 session with 5 pageviews
    for i in range(5):
        EventModel.create_event("pageview", "sess_avg_1", f"/page_{i}")
    overview = AggregationService.get_overview_metrics()
    assert overview["avg_views_per_session"] == 5.0

def test_aggregation_date_range_filtering():
    EventModel.create_event("pageview", "d_sess_1", "/home", created_at="2026-08-10 12:00:00")
    EventModel.create_event("pageview", "d_sess_2", "/home", created_at="2026-08-15 12:00:00")
    EventModel.create_event("pageview", "d_sess_3", "/home", created_at="2026-08-20 12:00:00")

    filtered = AggregationService.get_overview_metrics(start_date="2026-08-12", end_date="2026-08-18")
    assert filtered["pageviews"] == 1
    assert filtered["unique_visitors"] == 1

def test_timeseries_hourly_bucketing():
    EventModel.create_event("pageview", "ts_h_1", "/home", created_at="2026-08-20 14:15:00")
    EventModel.create_event("pageview", "ts_h_2", "/home", created_at="2026-08-20 14:45:00")
    EventModel.create_event("pageview", "ts_h_3", "/home", created_at="2026-08-20 15:10:00")

    ts = AggregationService.get_timeseries_traffic(start_date="2026-08-20", end_date="2026-08-20", interval="hour")
    assert len(ts) == 2
    assert ts[0]["bucket"] == "2026-08-20 14:00:00"
    assert ts[0]["pageviews"] == 2
    assert ts[1]["bucket"] == "2026-08-20 15:00:00"
    assert ts[1]["pageviews"] == 1

def test_timeseries_monthly_bucketing():
    EventModel.create_event("pageview", "ts_m_1", "/home", created_at="2026-07-15 10:00:00")
    EventModel.create_event("pageview", "ts_m_2", "/home", created_at="2026-08-15 10:00:00")

    ts = AggregationService.get_timeseries_traffic(interval="month")
    assert len(ts) == 2
    assert ts[0]["bucket"] == "2026-07-01"
    assert ts[1]["bucket"] == "2026-08-01"

def test_timeseries_empty_returns_empty_list():
    ts = AggregationService.get_timeseries_traffic(start_date="2025-01-01", end_date="2025-01-02")
    assert ts == []

def test_breakdowns_device_distribution_percentages():
    EventModel.create_event("pageview", "bd_d_1", "/home", device_type="desktop")
    EventModel.create_event("pageview", "bd_d_2", "/home", device_type="desktop")
    EventModel.create_event("pageview", "bd_d_3", "/home", device_type="mobile")
    EventModel.create_event("pageview", "bd_d_4", "/home", device_type="mobile")

    bds = AggregationService.get_breakdowns()
    devs = bds["devices"]
    assert len(devs) == 2
    assert devs[0]["percentage"] == 50.0
    assert devs[1]["percentage"] == 50.0

def test_breakdowns_browser_distribution():
    EventModel.create_event("pageview", "bd_b_1", "/home", browser="Chrome")
    EventModel.create_event("pageview", "bd_b_2", "/home", browser="Chrome")
    EventModel.create_event("pageview", "bd_b_3", "/home", browser="Safari")

    bds = AggregationService.get_breakdowns()
    browsers = bds["browsers"]
    assert browsers[0]["label"] == "Chrome"
    assert browsers[0]["count"] == 2
    assert browsers[0]["percentage"] == 66.67

def test_breakdowns_country_distribution():
    EventModel.create_event("pageview", "bd_c_1", "/home", country="United States")
    EventModel.create_event("pageview", "bd_c_2", "/home", country="Germany")
    EventModel.create_event("pageview", "bd_c_3", "/home", country="Japan")

    bds = AggregationService.get_breakdowns()
    assert len(bds["countries"]) == 3

def test_breakdowns_os_distribution():
    EventModel.create_event("pageview", "bd_os_1", "/home", os_name="Windows")
    EventModel.create_event("pageview", "bd_os_2", "/home", os_name="MacOS")
    bds = AggregationService.get_breakdowns()
    assert len(bds["operating_systems"]) == 2

def test_breakdowns_referrer_distribution():
    EventModel.create_event("pageview", "bd_r_1", "/home", referrer="https://google.com")
    EventModel.create_event("pageview", "bd_r_2", "/home", referrer=None)

    bds = AggregationService.get_breakdowns()
    labels = [r["label"] for r in bds["referrers"]]
    assert "https://google.com" in labels
    assert "Unknown" in labels

def test_top_pages_ranking_and_share():
    EventModel.create_event("pageview", "tp_1", "/docs")
    EventModel.create_event("pageview", "tp_2", "/docs")
    EventModel.create_event("pageview", "tp_3", "/docs")
    EventModel.create_event("pageview", "tp_4", "/pricing")

    top = AggregationService.get_top_pages(limit=10)
    assert top[0]["url_path"] == "/docs"
    assert top[0]["views"] == 3
    assert top[0]["share_pct"] == 75.0
    assert top[1]["url_path"] == "/pricing"
    assert top[1]["share_pct"] == 25.0

def test_top_pages_limit_respected():
    for i in range(10):
        EventModel.create_event("pageview", f"tpl_{i}", f"/page_{i}")
    top = AggregationService.get_top_pages(limit=3)
    assert len(top) == 3

def test_growth_deltas_positive_growth():
    # Previous period: 2026-08-01 to 2026-08-05 (10 views)
    for i in range(10):
        EventModel.create_event("pageview", f"prev_{i}", "/home", created_at="2026-08-03 10:00:00")
    # Current period: 2026-08-06 to 2026-08-10 (20 views -> +100% growth)
    for i in range(20):
        EventModel.create_event("pageview", f"curr_{i}", "/home", created_at="2026-08-08 10:00:00")

    overview = AggregationService.get_overview_metrics(start_date="2026-08-06", end_date="2026-08-10")
    deltas = overview["growth_deltas"]
    assert deltas["pageviews_delta_pct"] == 100.0
    assert deltas["previous_pageviews"] == 10

def test_growth_deltas_negative_growth():
    # Previous: 20 views
    for i in range(20):
        EventModel.create_event("pageview", f"neg_p_{i}", "/home", created_at="2026-08-03 10:00:00")
    # Current: 10 views (-50% drop)
    for i in range(10):
        EventModel.create_event("pageview", f"neg_c_{i}", "/home", created_at="2026-08-08 10:00:00")

    overview = AggregationService.get_overview_metrics(start_date="2026-08-06", end_date="2026-08-10")
    assert overview["growth_deltas"]["pageviews_delta_pct"] == -50.0

def test_growth_deltas_zero_previous_period():
    for i in range(5):
        EventModel.create_event("pageview", f"zero_{i}", "/home", created_at="2026-08-08 10:00:00")
    overview = AggregationService.get_overview_metrics(start_date="2026-08-06", end_date="2026-08-10")
    assert overview["growth_deltas"]["pageviews_delta_pct"] == 0.0

def test_aggregation_with_authenticated_users():
    EventModel.create_event("pageview", "auth_sess_1", "/dash", user_id="user_100")
    EventModel.create_event("pageview", "auth_sess_2", "/dash", user_id="user_100")
    EventModel.create_event("pageview", "auth_sess_3", "/dash", user_id="user_200")

    overview = AggregationService.get_overview_metrics()
    assert overview["unique_users"] == 2
    assert overview["unique_visitors"] == 3
