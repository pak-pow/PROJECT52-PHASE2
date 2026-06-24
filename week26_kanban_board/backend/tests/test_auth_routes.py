import pytest
from app.models import user_model

def test_register_success(client):
    res = client.post('/api/auth/register', json={
        'username': 'newuser',
        'password': 'password123'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert 'token' in data
    assert 'user' in data
    assert data['user']['username'] == 'newuser'

def test_register_missing_fields(client):
    res = client.post('/api/auth/register', json={
        'username': 'newuser'
    })
    assert res.status_code == 400
    assert 'error' in res.get_json()

def test_register_password_too_short(client):
    res = client.post('/api/auth/register', json={
        'username': 'newuser',
        'password': '123'
    })
    assert res.status_code == 400
    assert 'Password must be at least' in res.get_json()['error']

def test_register_duplicate_username(client):
    client.post('/api/auth/register', json={
        'username': 'duplicate',
        'password': 'password123'
    })
    res = client.post('/api/auth/register', json={
        'username': 'duplicate',
        'password': 'password456'
    })
    assert res.status_code == 400
    assert 'Username is already taken' in res.get_json()['error']

def test_login_success(client):
    # Register first
    client.post('/api/auth/register', json={
        'username': 'loginuser',
        'password': 'password123'
    })
    
    # Login
    res = client.post('/api/auth/login', json={
        'username': 'loginuser',
        'password': 'password123'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert 'token' in data
    assert 'user' in data
    assert data['user']['username'] == 'loginuser'

def test_login_invalid_password(client):
    client.post('/api/auth/register', json={
        'username': 'loginuser2',
        'password': 'password123'
    })
    res = client.post('/api/auth/login', json={
        'username': 'loginuser2',
        'password': 'wrongpassword'
    })
    assert res.status_code == 401
    assert 'Invalid username or password' in res.get_json()['error']

def test_logout(client):
    reg = client.post('/api/auth/register', json={
        'username': 'logoutuser',
        'password': 'password123'
    })
    token = reg.get_json()['token']
    
    res = client.post('/api/auth/logout', headers={
        'Authorization': f'Bearer {token}'
    })
    assert res.status_code == 204

    # Now call me and it should be unauthorized
    res_me = client.get('/api/auth/me', headers={
        'Authorization': f'Bearer {token}'
    })
    assert res_me.status_code == 401

def test_me_authorized(client):
    reg = client.post('/api/auth/register', json={
        'username': 'meuser',
        'password': 'password123'
    })
    token = reg.get_json()['token']
    
    res = client.get('/api/auth/me', headers={
        'Authorization': f'Bearer {token}'
    })
    assert res.status_code == 200
    assert res.get_json()['user']['username'] == 'meuser'

def test_me_unauthorized(client):
    res = client.get('/api/auth/me')
    assert res.status_code == 401
