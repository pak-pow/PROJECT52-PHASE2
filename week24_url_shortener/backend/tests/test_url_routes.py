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
    """Ensure expired links return a 410 Gone status."""
    
    post_res = client.post('/api/shorten', json={
        'url': 'https://www.topsecret.com',
        'expires_in_hours': -1 
    })
    short_code = post_res.get_json()['short_code']
    get_res = client.get(f'/{short_code}')
    assert get_res.status_code == 410