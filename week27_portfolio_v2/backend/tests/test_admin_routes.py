"""
Tests for /api/admin/* endpoints
"""


class TestAdminLogin:

    def test_login_correct_credentials_returns_200(self, client):
        res = client.post("/api/admin/login", json={
            "username": "admin", "password": "admin123"
        })
        assert res.status_code == 200
        assert "token" in res.get_json()

    def test_login_wrong_password_returns_401(self, client):
        res = client.post("/api/admin/login", json={
            "username": "admin", "password": "wrongpassword"
        })
        assert res.status_code == 401

    def test_login_wrong_username_returns_401(self, client):
        res = client.post("/api/admin/login", json={
            "username": "hacker", "password": "admin123"
        })
        assert res.status_code == 401

    def test_login_empty_body_returns_401(self, client):
        res = client.post("/api/admin/login", json={})
        assert res.status_code == 401


class TestAdminLogout:

    def test_logout_with_valid_token_returns_200(self, client, auth_headers):
        res = client.post("/api/admin/logout", headers=auth_headers)
        assert res.status_code == 200

    def test_logout_without_token_returns_401(self, client):
        res = client.post("/api/admin/logout")
        assert res.status_code == 401

    def test_token_invalid_after_logout(self, client, auth_headers):
        client.post("/api/admin/logout", headers=auth_headers)
        # Try using the same token again
        res = client.get("/api/admin/messages", headers=auth_headers)
        assert res.status_code == 401


class TestAdminMessages:

    def _submit_message(self, client, name="Bob"):
        client.post("/api/contact", json={
            "name":    name,
            "email":   f"{name.lower()}@example.com",
            "subject": "Test",
            "message": "Hello from test",
        })

    def test_list_messages_without_auth_returns_401(self, client):
        res = client.get("/api/admin/messages")
        assert res.status_code == 401

    def test_list_messages_with_auth_returns_200(self, client, auth_headers):
        res = client.get("/api/admin/messages", headers=auth_headers)
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_list_messages_returns_submitted_messages(self, client, auth_headers):
        self._submit_message(client, "TestUser")
        res = client.get("/api/admin/messages", headers=auth_headers)
        data = res.get_json()
        assert any(m["name"] == "TestUser" for m in data)

    def test_new_message_is_unread_by_default(self, client, auth_headers):
        self._submit_message(client, "Unread")
        res = client.get("/api/admin/messages", headers=auth_headers)
        messages = [m for m in res.get_json() if m["name"] == "Unread"]
        assert messages[0]["is_read"] is False

    def test_toggle_read_returns_200(self, client, auth_headers):
        self._submit_message(client, "Reader")
        messages = client.get(
            "/api/admin/messages", headers=auth_headers
        ).get_json()
        msg_id = next(m["id"] for m in messages if m["name"] == "Reader")

        res = client.patch(
            f"/api/admin/messages/{msg_id}/read", headers=auth_headers
        )
        assert res.status_code == 200
        assert res.get_json()["is_read"] is True

    def test_toggle_read_nonexistent_returns_404(self, client, auth_headers):
        res = client.patch(
            "/api/admin/messages/99999/read", headers=auth_headers
        )
        assert res.status_code == 404

    def test_delete_message_returns_204(self, client, auth_headers):
        self._submit_message(client, "Deleter")
        messages = client.get(
            "/api/admin/messages", headers=auth_headers
        ).get_json()
        msg_id = next(m["id"] for m in messages if m["name"] == "Deleter")

        res = client.delete(
            f"/api/admin/messages/{msg_id}", headers=auth_headers
        )
        assert res.status_code == 204

    def test_delete_nonexistent_message_returns_404(self, client, auth_headers):
        res = client.delete(
            "/api/admin/messages/99999", headers=auth_headers
        )
        assert res.status_code == 404

    def test_delete_without_auth_returns_401(self, client):
        res = client.delete("/api/admin/messages/1")
        assert res.status_code == 401
