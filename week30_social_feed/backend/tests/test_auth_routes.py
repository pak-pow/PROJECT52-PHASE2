"""Tests for auth routes: register, login, logout, /me."""


def test_register_success(client):
    resp = client.post("/api/auth/register", json={
        "username": "newuser",
        "display_name": "New User",
        "password": "password123",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert "token" in data
    assert data["username"] == "newuser"


def test_register_duplicate_username(client):
    payload = {"username": "alice", "display_name": "Alice", "password": "pass123"}
    client.post("/api/auth/register", json=payload)
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 409


def test_register_username_too_short(client):
    resp = client.post("/api/auth/register", json={
        "username": "ab",
        "password": "pass123",
    })
    assert resp.status_code == 400


def test_register_password_too_short(client):
    resp = client.post("/api/auth/register", json={
        "username": "validuser",
        "password": "ab",
    })
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/api/auth/register", json={
        "username": "logintest",
        "password": "password123",
    })
    resp = client.post("/api/auth/login", json={
        "username": "logintest",
        "password": "password123",
    })
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "username": "wrongpass",
        "password": "correctpass",
    })
    resp = client.post("/api/auth/login", json={
        "username": "wrongpass",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_me_requires_auth(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_returns_user(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["username"] == "testuser"


def test_logout(client, auth_headers):
    resp = client.post("/api/auth/logout", headers=auth_headers)
    assert resp.status_code == 200
    # Token should now be invalid
    resp2 = client.get("/api/auth/me", headers=auth_headers)
    assert resp2.status_code == 401
