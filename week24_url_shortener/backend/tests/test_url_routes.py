import pytest #type: ignore

def test_api_shorten_success(client):
    """Test POST /api/shorten with a valid URL."""
    response = client.post('/api/shorten', json={
        'url': 'https://www.docker.com'
    })
    
    assert response.status_code == 201 
    data = response.get_json()
    assert 'short_code' in data
    assert data['original_url'] == 'https://www.docker.com'

def test_api_shorten_invalid_missing_key(client):
    """Test POST /api/shorten to ensure it rejects bad JSON payloads."""
    response = client.post('/api/shorten', json={
        'wrong_key_name': 'https://www.docker.com'
    })
    
    assert response.status_code == 400 

def test_rate_limiting_blocks_spam(client):
    """Ensure a single IP cannot spam the shorten endpoint."""
    
    for i in range(5):
        res = client.post('/api/shorten', json={'url': f'https://www.example.com/{i}'})
        assert res.status_code == 201

    res = client.post('/api/shorten', json={'url': 'https://www.example.com/spam'})
    assert res.status_code == 429
    
    
def test_self_destructing_link_returns_410(client):
    """Ensure expired links return a 410 Gone status.
    
    Strategy: create a link with 1-hour expiry, then patch datetime.now() in the 
    service module to return a time 2 hours in the future so the expiry check fires.
    """
    from unittest.mock import patch
    from datetime import datetime, timezone, timedelta

    post_res = client.post('/api/shorten', json={
        'url': 'https://www.topsecret.com',
        'expires_in_hours': 1
    })
    assert post_res.status_code == 201
    short_code = post_res.get_json()['short_code']

    # Simulate being 2 hours in the future — link is now expired
    future_time = datetime.now(timezone.utc) + timedelta(hours=2)
    with patch('app.services.url_service.datetime') as mock_dt:
        mock_dt.fromisoformat = datetime.fromisoformat
        mock_dt.now.return_value = future_time

        get_res = client.get(f'/{short_code}')
        assert get_res.status_code == 410