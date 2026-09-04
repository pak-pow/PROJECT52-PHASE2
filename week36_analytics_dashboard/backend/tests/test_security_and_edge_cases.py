import pytest
import threading
from app.models.event_model import EventModel
from app.models.funnel_model import FunnelModel
from app.services.aggregation_service import AggregationService
from app.services.serializers import serialize_event
from app.db import get_db_connection

def test_sql_injection_resilience_in_date_filter(client):
    sqli_payload = "2026-08-01' OR '1'='1"
    res = client.get(f"/api/analytics/overview?start_date={sqli_payload}")
    assert res.status_code == 200
    data = res.get_json()
    assert "metrics" in data

def test_sql_injection_resilience_in_interval_param(client):
    sqli_payload = "day'; DROP TABLE events; --"
    res = client.get(f"/api/analytics/timeseries?interval={sqli_payload}")
    assert res.status_code == 200
    # Should fallback to 'day' safely
    assert res.get_json()["interval"] == "day"

def test_sql_injection_in_event_name_creation():
    sqli_name = "test_event'); DROP TABLE events; --"
    evt = EventModel.create_event(sqli_name, "sqli_sess", "/home")
    assert evt is not None
    assert evt["event_name"] == sqli_name

    # Verify events table still exists and is intact
    assert EventModel.get_total_count() >= 1

def test_xss_payload_in_url_path(client):
    xss_path = "/search?q=<script>alert('xss')</script>"
    res = client.post("/api/events", json={
        "event_name": "pageview",
        "session_id": "xss_sess",
        "url_path": xss_path
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["event"]["url_path"] == xss_path

def test_xss_payload_in_metadata_json(client):
    xss_meta = {"user_input": "<img src=x onerror=alert(1)>"}
    res = client.post("/api/events", json={
        "event_name": "click",
        "session_id": "xss_meta_sess",
        "url_path": "/profile",
        "metadata": xss_meta
    })
    assert res.status_code == 201
    assert res.get_json()["event"]["metadata"]["user_input"] == "<img src=x onerror=alert(1)>"

def test_large_content_payload_handling():
    large_meta = {f"key_{i}": f"value_string_payload_{i}" * 10 for i in range(100)} # ~15 KB metadata
    evt = EventModel.create_event(
        event_name="large_payload_event",
        session_id="large_sess",
        url_path="/very/long/path/with/lots/of/segments/" * 5,
        metadata=large_meta
    )
    serialized = serialize_event(evt)
    assert len(serialized["metadata"]) == 100

def test_concurrent_event_ingestion_thread_safety():
    errors = []

    def ingest_worker(worker_id):
        try:
            for i in range(10):
                EventModel.create_event(
                    event_name="concurrent_event",
                    session_id=f"thread_{worker_id}",
                    url_path=f"/thread_path_{i}"
                )
        except Exception as e:
            errors.append(str(e))

    threads = [threading.Thread(target=ingest_worker, args=(w,)) for w in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0

def test_corrupted_date_format_fallback():
    # Passing garbage date string should not crash aggregation
    res = AggregationService.get_overview_metrics(start_date="NOT_A_DATE", end_date="ALSO_NOT_A_DATE")
    assert "pageviews" in res
    assert "growth_deltas" in res

def test_foreign_key_cascade_deletion():
    f = FunnelModel.create_funnel("Cascade Funnel", steps=[
        {"step_name": "Step 1", "event_name": "step1"},
        {"step_name": "Step 2", "event_name": "step2"}
    ])
    funnel_id = f["id"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as c FROM funnel_steps WHERE funnel_id = ?", (funnel_id,))
    assert cursor.fetchone()["c"] == 2

    # Delete parent funnel
    cursor.execute("DELETE FROM funnels WHERE id = ?", (funnel_id,))
    conn.commit()

    # Steps should be cascaded and deleted automatically
    cursor.execute("SELECT COUNT(*) as c FROM funnel_steps WHERE funnel_id = ?", (funnel_id,))
    assert cursor.fetchone()["c"] == 0
    conn.close()

def test_cors_headers_present_on_api_responses(client):
    res = client.get("/api/health")
    assert res.headers.get("Access-Control-Allow-Origin") == "*"

    res_opt = client.options("/api/events")
    assert res_opt.status_code in [200, 204]
    assert res_opt.headers.get("Access-Control-Allow-Origin") == "*"
