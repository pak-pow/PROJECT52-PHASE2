"""
Tests for POST /api/contact
"""


class TestContactSubmit:

    def test_valid_submission_returns_201(self, client):
        res = client.post("/api/contact", json={
            "name":    "Alice",
            "email":   "alice@example.com",
            "subject": "Hello",
            "message": "Great portfolio!",
        })
        assert res.status_code == 201
        assert "Message sent" in res.get_json()["message"]

    def test_missing_name_returns_400(self, client):
        res = client.post("/api/contact", json={
            "email":   "alice@example.com",
            "subject": "Hello",
            "message": "Hi there",
        })
        assert res.status_code == 400
        assert "name" in res.get_json()["error"]

    def test_missing_email_returns_400(self, client):
        res = client.post("/api/contact", json={
            "name":    "Alice",
            "subject": "Hello",
            "message": "Hi there",
        })
        assert res.status_code == 400
        assert "email" in res.get_json()["error"]

    def test_invalid_email_format_returns_400(self, client):
        res = client.post("/api/contact", json={
            "name":    "Alice",
            "email":   "not-an-email",
            "subject": "Hello",
            "message": "Hi there",
        })
        assert res.status_code == 400

    def test_missing_subject_returns_400(self, client):
        res = client.post("/api/contact", json={
            "name":    "Alice",
            "email":   "alice@example.com",
            "message": "Hi there",
        })
        assert res.status_code == 400
        assert "subject" in res.get_json()["error"]

    def test_missing_message_returns_400(self, client):
        res = client.post("/api/contact", json={
            "name":    "Alice",
            "email":   "alice@example.com",
            "subject": "Hello",
        })
        assert res.status_code == 400
        assert "message" in res.get_json()["error"]

    def test_empty_body_returns_400(self, client):
        res = client.post("/api/contact", json={})
        assert res.status_code == 400

    def test_non_json_body_returns_400(self, client):
        res = client.post(
            "/api/contact",
            data="name=Alice",
            content_type="text/plain",
        )
        assert res.status_code == 400
