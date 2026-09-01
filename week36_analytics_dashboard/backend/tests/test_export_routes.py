import pytest

def test_export_csv_default_traffic(client):
    client.post("/api/events", json={"event_name": "pageview", "session_id": "csv_1", "url_path": "/dash"})
    res = client.get("/api/export/csv")
    assert res.status_code == 200
    assert "text/csv" in res.content_type
    assert "attachment; filename=analytics_export_traffic.csv" in res.headers["Content-Disposition"]
    
    csv_text = res.get_data(as_text=True)
    assert "Date Bucket,Pageviews,Total Events,Unique Visitors" in csv_text

def test_export_csv_raw_events(client):
    client.post("/api/events", json={"event_name": "purchase", "session_id": "csv_raw_1", "url_path": "/buy", "user_id": "usr_99"})
    res = client.get("/api/export/csv?type=events")
    assert res.status_code == 200
    assert "text/csv" in res.content_type
    assert "attachment; filename=analytics_export_events.csv" in res.headers["Content-Disposition"]

    csv_text = res.get_data(as_text=True)
    assert "ID,Event Name,Session ID,User ID,URL Path,Referrer,Device,Browser,OS,Country,Timestamp" in csv_text
    assert "purchase" in csv_text
    assert "csv_raw_1" in csv_text

def test_export_csv_with_date_range(client):
    res = client.get("/api/export/csv?start_date=2026-08-01&end_date=2026-08-30")
    assert res.status_code == 200
    assert "text/csv" in res.content_type

def test_export_json_endpoint_structure(client):
    client.post("/api/events", json={"event_name": "pageview", "session_id": "json_1", "url_path": "/home"})
    res = client.get("/api/export/json")
    assert res.status_code == 200
    data = res.get_json()
    assert "timeframe" in data
    assert "overview" in data
    assert "timeseries" in data
    assert "breakdowns" in data
    assert "top_pages" in data

def test_export_json_overview_fields(client):
    res = client.get("/api/export/json")
    assert res.status_code == 200
    ov = res.get_json()["overview"]
    assert "total_events" in ov
    assert "pageviews" in ov
    assert "unique_visitors" in ov
    assert "bounce_rate_pct" in ov

def test_export_json_breakdowns_fields(client):
    res = client.get("/api/export/json")
    assert res.status_code == 200
    bd = res.get_json()["breakdowns"]
    assert "devices" in bd
    assert "browsers" in bd
    assert "operating_systems" in bd
    assert "countries" in bd
    assert "referrers" in bd

def test_export_json_with_custom_dates(client):
    res = client.get("/api/export/json?start_date=2026-08-01&end_date=2026-08-15")
    assert res.status_code == 200
    tf = res.get_json()["timeframe"]
    assert tf["start_date"] == "2026-08-01"
    assert tf["end_date"] == "2026-08-15"

def test_export_csv_empty_database(client):
    res = client.get("/api/export/csv?type=traffic")
    assert res.status_code == 200
    csv_text = res.get_data(as_text=True)
    assert "Date Bucket,Pageviews,Total Events,Unique Visitors" in csv_text

def test_export_csv_events_empty_database(client):
    res = client.get("/api/export/csv?type=events")
    assert res.status_code == 200
    csv_text = res.get_data(as_text=True)
    assert "ID,Event Name,Session ID,User ID,URL Path,Referrer,Device,Browser,OS,Country,Timestamp" in csv_text

def test_export_json_top_pages_limit(client):
    for i in range(5):
        client.post("/api/events", json={"event_name": "pageview", "session_id": f"s_{i}", "url_path": f"/page_{i}"})
    res = client.get("/api/export/json")
    assert res.status_code == 200
    pages = res.get_json()["top_pages"]
    assert len(pages) <= 20
