"""
Tests for POST /api/auth/register and POST /api/auth/login and GET /api/auth/me
"""
import pytest  # type: ignore


# ─── REGISTRATION ────────────────────────────────────────────────────────────

class TestRegister:
    """Tests for POST /api/auth/register"""

    def test_register_success(self, client):
        """A new user with valid credentials should be created with a 201."""
        res = client.post('/api/auth/register', json={
            "username": "newuser",
            "password": "SecurePass1"
        })
        assert res.status_code == 201
        assert "created" in res.get_json()["message"].lower()

    def test_register_duplicate_username_returns_409(self, client):
        """Registering the same username twice should return 409 Conflict."""
        payload = {"username": "dupeuser", "password": "SecurePass1"}
        client.post('/api/auth/register', json=payload)
        res = client.post('/api/auth/register', json=payload)
        assert res.status_code == 409
        assert "already exists" in res.get_json()["error"].lower()

    def test_register_missing_username_returns_400(self, client):
        """Missing username field should return 400."""
        res = client.post('/api/auth/register', json={"password": "SecurePass1"})
        assert res.status_code == 400

    def test_register_missing_password_returns_400(self, client):
        """Missing password field should return 400."""
        res = client.post('/api/auth/register', json={"username": "newuser"})
        assert res.status_code == 400

    def test_register_username_too_short_returns_400(self, client):
        """Username under 3 characters should be rejected with 400."""
        res = client.post('/api/auth/register', json={
            "username": "ab",
            "password": "SecurePass1"
        })
        assert res.status_code == 400
        assert "3" in res.get_json()["error"]

    def test_register_password_too_short_returns_400(self, client):
        """Password under 8 characters should be rejected with 400."""
        res = client.post('/api/auth/register', json={
            "username": "validuser",
            "password": "short"
        })
        assert res.status_code == 400
        assert "8" in res.get_json()["error"]

    def test_register_username_with_only_whitespace_returns_400(self, client):
        """A username that is only spaces should be rejected after stripping."""
        res = client.post('/api/auth/register', json={
            "username": "   ",
            "password": "SecurePass1"
        })
        assert res.status_code == 400

    def test_register_no_body_returns_400(self, client):
        """Request with no JSON body should return 4xx (Flask returns 415 Unsupported Media Type)."""
        res = client.post('/api/auth/register')
        assert res.status_code in (400, 415)


# ─── LOGIN ────────────────────────────────────────────────────────────────────

class TestLogin:
    """Tests for POST /api/auth/login"""

    def test_login_success_returns_token(self, client):
        """A valid login should return a 200 with an access_token."""
        client.post('/api/auth/register', json={
            "username": "loginuser",
            "password": "SecurePass1"
        })
        res = client.post('/api/auth/login', json={
            "username": "loginuser",
            "password": "SecurePass1"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert "access_token" in data
        assert len(data["access_token"]) > 0

    def test_login_wrong_password_returns_401(self, client):
        """A login with the wrong password should return 401."""
        client.post('/api/auth/register', json={
            "username": "loginuser2",
            "password": "SecurePass1"
        })
        res = client.post('/api/auth/login', json={
            "username": "loginuser2",
            "password": "WrongPassword"
        })
        assert res.status_code == 401

    def test_login_nonexistent_user_returns_401(self, client):
        """Logging in with a username that doesn't exist should return 401."""
        res = client.post('/api/auth/login', json={
            "username": "ghost",
            "password": "SecurePass1"
        })
        assert res.status_code == 401

    def test_login_missing_fields_returns_400(self, client):
        """Login request with no username/password should return 400."""
        res = client.post('/api/auth/login', json={"username": "testadmin"})
        assert res.status_code == 400


# ─── /ME ROUTE ───────────────────────────────────────────────────────────────

class TestMe:
    """Tests for GET /api/auth/me"""

    def test_me_returns_user_profile(self, client, auth_headers):
        """An authenticated request should return the user's profile."""
        res = client.get('/api/auth/me', headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert data["username"] == "testadmin"
        assert "id" in data
        assert "created_at" in data

    def test_me_does_not_expose_password_hash(self, client, auth_headers):
        """The /me response must never include the password_hash field."""
        res = client.get('/api/auth/me', headers=auth_headers)
        assert "password_hash" not in res.get_json()

    def test_me_without_token_returns_401(self, client):
        """Unauthenticated request to /me should return 401."""
        res = client.get('/api/auth/me')
        assert res.status_code == 401
