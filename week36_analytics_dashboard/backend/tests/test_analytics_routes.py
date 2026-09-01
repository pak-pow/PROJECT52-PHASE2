import pytest

def test_track_event_success(client):
    res = client.post("/api/events", json={
        "event_name": "pageview",
        "session_id": "route_sess_1",
        "url_path": "/dashboard",
        "user_id": "usr_10",
        "referrer": "https://google.com",
        "metadata": {"source": "campaign_a"}
    }, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"})

    assert res.status_code == 201
    data = res.get_json()
    assert data["message"] == "Event recorded successfully."
    assert data["event"]["event_name"] == "pageview"
    assert data["event"]["browser"] == "Chrome"
    assert data["event"]["metadata"]["source"] == "campaign_a"

def test_track_event_missing_event_name(client):
    res = client.post("/api/events", json={
        "session_id": "route_sess_2"
    })
    assert res.status_code == 400
    assert "required" in res.get_json()["error"]

def test_track_event_missing_session_id(client):
    res = client.post("/api/events", json={
        "event_name": "click"
    })
    assert res.status_code == 400
    assert "required" in res.get_json()["error"]

def test_track_events_batch_success(client):
    res = client.post("/api/events/batch", json={
        "events": [
            {"event_name": "pageview", "session_id": "batch_1", "url_path": "/home"},
            {"event_name": "click", "session_id": "batch_1", "url_path": "/home"},
            {"event_name": "pageview", "session_id": "batch_2", "url_path": "/pricing"}
        ]
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["count"] == 3
    assert len(data["events"]) == 3

def test_track_events_batch_empty_list_400(client):
    res = client.post("/api/events/batch", json={"events": []})
    assert res.status_code == 400

def test_track_events_batch_invalid_payload_400(client):
    res = client.post("/api/events/batch", json={"events": "NOT_A_LIST"})
    assert res.status_code == 400

def test_get_live_stream_endpoint(client):
    client.post("/api/events", json={"event_name": "live_test", "session_id": "ls_1", "url_path": "/live"})
    res = client.get("/api/events/live?limit=5")
    assert res.status_code == 200
    data = res.get_json()
    assert data["limit"] == 5
    assert data["count"] >= 1

def test_get_analytics_overview_endpoint(client):
    client.post("/api/events", json={"event_name": "pageview", "session_id": "ov_1", "url_path": "/test"})
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200
    data = res.get_json()
    assert "metrics" in data
    assert "pageviews" in data["metrics"]
    assert "unique_visitors" in data["metrics"]
    assert "bounce_rate_pct" in data["metrics"]

def test_get_analytics_timeseries_daily_endpoint(client):
    client.post("/api/events", json={"event_name": "pageview", "session_id": "ts_1", "url_path": "/ts"})
    res = client.get("/api/analytics/timeseries?interval=day")
    assert res.status_code == 200
    data = res.get_json()
    assert data["interval"] == "day"
    assert "data" in data

def test_get_analytics_timeseries_hourly_endpoint(client):
    res = client.get("/api/analytics/timeseries?interval=hour")
    assert res.status_code == 200
    assert res.get_json()["interval"] == "hour"

def test_get_analytics_timeseries_invalid_interval_fallback(client):
    res = client.get("/api/analytics/timeseries?interval=invalid_interval_xyz")
    assert res.status_code == 200
    assert res.get_json()["interval"] == "day"

def test_get_analytics_breakdowns_endpoint(client):
    client.post("/api/events", json={"event_name": "pageview", "session_id": "bd_1", "url_path": "/bd"})
    res = client.get("/api/analytics/breakdown")
    assert res.status_code == 200
    data = res.get_json()
    assert "devices" in data
    assert "browsers" in data
    assert "operating_systems" in data
    assert "countries" in data
    assert "referrers" in data

def test_get_analytics_top_pages_endpoint(client):
    client.post("/api/events", json={"event_name": "pageview", "session_id": "tp_1", "url_path": "/page_a"})
    res = client.get("/api/analytics/top-pages?limit=5")
    assert res.status_code == 200
    data = res.get_json()
    assert data["limit"] == 5
    assert len(data["pages"]) >= 1

def test_create_funnel_endpoint_success(client):
    res = client.post("/api/funnels", json={
        "name": "API Onboarding Funnel",
        "description": "Onboarding flow",
        "steps": [
            {"step_name": "Step 1", "event_name": "view_welcome"},
            {"step_name": "Step 2", "event_name": "click_start"}
        ]
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["funnel"]["name"] == "API Onboarding Funnel"
    assert len(data["funnel"]["steps"]) == 2

def test_create_funnel_missing_name_400(client):
    res = client.post("/api/funnels", json={
        "steps": [{"step_name": "Step 1", "event_name": "view"}]
    })
    assert res.status_code == 400

def test_create_funnel_missing_steps_400(client):
    res = client.post("/api/funnels", json={
        "name": "Empty Step Funnel",
        "steps": []
    })
    assert res.status_code == 400

def test_create_funnel_duplicate_name_409(client):
    client.post("/api/funnels", json={
        "name": "Duplicate Funnel Name",
        "steps": [{"step_name": "S1", "event_name": "E1"}]
    })
    res = client.post("/api/funnels", json={
        "name": "Duplicate Funnel Name",
        "steps": [{"step_name": "S1", "event_name": "E1"}]
    })
    assert res.status_code == 409
    assert "already exists" in res.get_json()["error"]

def test_get_funnel_details_endpoint(client):
    f_res = client.post("/api/funnels", json={
        "name": "Details Funnel",
        "steps": [{"step_name": "S1", "event_name": "E1"}]
    })
    funnel_id = f_res.get_json()["funnel"]["id"]

    res = client.get(f"/api/funnels/{funnel_id}")
    assert res.status_code == 200
    assert res.get_json()["name"] == "Details Funnel"

def test_get_funnel_details_not_found_404(client):
    res = client.get("/api/funnels/99999")
    assert res.status_code == 404

def test_get_funnel_metrics_endpoint(client):
    f_res = client.post("/api/funnels", json={
        "name": "Metrics Funnel",
        "steps": [{"step_name": "Step 1", "event_name": "view_m"}]
    })
    funnel_id = f_res.get_json()["funnel"]["id"]

    client.post("/api/events", json={"event_name": "view_m", "session_id": "met_s1", "url_path": "/"})

    res = client.get(f"/api/funnels/{funnel_id}/metrics")
    assert res.status_code == 200
    data = res.get_json()
    assert data["initial_visitors"] == 1
    assert data["overall_conversion_pct"] == 100.0
