import os
import sys
import time
import pytest

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.services.token_bucket import TokenBucket
from app.services.sliding_window import SlidingWindowLog
from app.services.storage_adapter import storage

@pytest.fixture
def app_instance():
    app = create_app()
    app.config["TESTING"] = True
    storage.clear()
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

def test_token_bucket_unit():
    bucket = TokenBucket(capacity=3, fill_rate=1.0)
    # Consume 3 tokens
    allowed1, rem1, _ = bucket.consume(1)
    allowed2, rem2, _ = bucket.consume(1)
    allowed3, rem3, _ = bucket.consume(1)
    assert allowed1 and allowed2 and allowed3
    assert int(rem3) == 0

    # 4th request should be denied
    allowed4, _, wait_time = bucket.consume(1)
    assert not allowed4
    assert wait_time > 0

def test_sliding_window_log_unit():
    log = SlidingWindowLog(limit=2, window_seconds=2.0)
    allowed1, rem1, _ = log.is_allowed()
    allowed2, rem2, _ = log.is_allowed()
    allowed3, rem3, retry_after = log.is_allowed()

    assert allowed1 and allowed2
    assert not allowed3
    assert rem3 == 0
    assert retry_after > 0

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"

def test_rate_limit_burst_and_headers(client):
    # Route limit: 5 reqs / 10 sec
    for i in range(5):
        res = client.get("/api/data/burst-test")
        assert res.status_code == 200
        assert "X-RateLimit-Remaining" in res.headers
        assert "X-RateLimit-Limit" in res.headers

    # 6th request should return 429 Too Many Requests
    blocked = client.get("/api/data/burst-test")
    assert blocked.status_code == 429
    assert blocked.headers["X-RateLimit-Remaining"] == "0"
    assert "Retry-After" in blocked.headers
    data = blocked.get_json()
    assert data["error"] == "Too Many Requests"

def test_sliding_window_endpoint_limit(client):
    # Route limit: 5 reqs / 10 sec
    for i in range(5):
        res = client.get("/api/sliding/test")
        assert res.status_code == 200

    blocked = client.get("/api/sliding/test")
    assert blocked.status_code == 429
    assert blocked.get_json()["error"] == "Too Many Requests"

def test_api_key_issuance_and_status(client):
    # Issue Enterprise API Key
    res = client.post("/api/auth/api-key", json={"tier": "enterprise"})
    assert res.status_code == 201
    data = res.get_json()
    assert "api_key" in data
    assert data["tier"] == "enterprise"
    assert data["rate_limit"]["capacity"] == 100

    api_key = data["api_key"]
    status_res = client.get("/api/auth/api-key/status", headers={"X-API-Key": api_key})
    assert status_res.status_code == 200
    assert status_res.get_json()["capacity"] == 100

def test_tier_based_rate_limiting(client):
    # Test pre-seeded Pro key (capacity 30)
    pro_key = "demo-pro-key"
    res = client.get("/api/tier/data", headers={"X-API-Key": pro_key})
    assert res.status_code == 200
    assert res.headers["X-RateLimit-Limit"] == "30"

def test_sliding_window_log_eviction():
    log = SlidingWindowLog(limit=1, window_seconds=0.2)
    allowed1, _, _ = log.is_allowed()
    assert allowed1

    # Immediate second request should fail
    allowed2, _, _ = log.is_allowed()
    assert not allowed2

    # Wait for window eviction (0.25s)
    time.sleep(0.25)
    allowed3, _, _ = log.is_allowed()
    assert allowed3

def test_heavy_action_strict_limit(client):
    # Route limit: 2 reqs / 30 sec
    res1 = client.get("/api/action/heavy")
    res2 = client.get("/api/action/heavy")
    res3 = client.get("/api/action/heavy")

    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res3.status_code == 429
    assert "Retry-After" in res3.headers
