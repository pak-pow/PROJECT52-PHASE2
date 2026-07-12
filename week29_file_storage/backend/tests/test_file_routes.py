import io


# ═══════════════════════════════════════════════════════════════
#  Auth Tests
# ═══════════════════════════════════════════════════════════════

class TestAuth:
    """Tests for /api/auth/* endpoints."""

    def test_register_success(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "newuser",
            "password": "password123",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert "token" in data
        assert data["username"] == "newuser"

    def test_register_duplicate_username(self, client):
        client.post("/api/auth/register", json={
            "username": "dup_user", "password": "password123",
        })
        resp = client.post("/api/auth/register", json={
            "username": "dup_user", "password": "password456",
        })
        assert resp.status_code == 409

    def test_register_short_username(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "ab", "password": "password123",
        })
        assert resp.status_code == 400

    def test_register_short_password(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "validuser", "password": "123",
        })
        assert resp.status_code == 400

    def test_login_success(self, client):
        client.post("/api/auth/register", json={
            "username": "loginuser", "password": "password123",
        })
        resp = client.post("/api/auth/login", json={
            "username": "loginuser", "password": "password123",
        })
        assert resp.status_code == 200
        assert "token" in resp.get_json()

    def test_login_wrong_password(self, client):
        client.post("/api/auth/register", json={
            "username": "wrongpw", "password": "password123",
        })
        resp = client.post("/api/auth/login", json={
            "username": "wrongpw", "password": "wrong",
        })
        assert resp.status_code == 401

    def test_logout(self, client, auth_header):
        resp = client.post("/api/auth/logout", headers=auth_header)
        assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════
#  File Upload Tests
# ═══════════════════════════════════════════════════════════════

class TestFileUpload:
    """Tests for POST /api/files/upload."""

    def test_upload_requires_auth(self, client):
        resp = client.post("/api/files/upload")
        assert resp.status_code == 401

    def test_upload_no_files(self, client, auth_header):
        resp = client.post("/api/files/upload", headers=auth_header)
        assert resp.status_code == 400

    def test_upload_text_file(self, client, auth_header):
        data = {"files": (io.BytesIO(b"hello world"), "test.txt", "text/plain")}
        resp = client.post(
            "/api/files/upload",
            headers=auth_header,
            data=data,
            content_type="multipart/form-data",
        )
        assert resp.status_code == 201
        body = resp.get_json()
        assert len(body["uploaded"]) == 1
        assert body["uploaded"][0]["category"] == "document"

    def test_upload_invalid_type(self, client, auth_header):
        data = {"files": (io.BytesIO(b"\x00\x01"), "hack.exe", "application/x-executable")}
        resp = client.post(
            "/api/files/upload",
            headers=auth_header,
            data=data,
            content_type="multipart/form-data",
        )
        body = resp.get_json()
        assert len(body["errors"]) == 1


# ═══════════════════════════════════════════════════════════════
#  File List / Get / Delete Tests
# ═══════════════════════════════════════════════════════════════

class TestFileOperations:
    """Tests for GET/DELETE /api/files/*."""

    def _upload(self, client, headers, content=b"data", name="file.txt", mime="text/plain"):
        return client.post(
            "/api/files/upload",
            headers=headers,
            data={"files": (io.BytesIO(content), name, mime)},
            content_type="multipart/form-data",
        )

    def test_list_empty(self, client, auth_header):
        resp = client.get("/api/files", headers=auth_header)
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_after_upload(self, client, auth_header):
        self._upload(client, auth_header)
        resp = client.get("/api/files", headers=auth_header)
        assert len(resp.get_json()) == 1

    def test_list_category_filter(self, client, auth_header):
        self._upload(client, auth_header, name="doc.txt", mime="text/plain")
        resp = client.get("/api/files?category=document", headers=auth_header)
        assert len(resp.get_json()) == 1
        resp2 = client.get("/api/files?category=image", headers=auth_header)
        assert len(resp2.get_json()) == 0

    def test_get_single_file(self, client, auth_header):
        up = self._upload(client, auth_header)
        file_id = up.get_json()["uploaded"][0]["id"]
        resp = client.get(f"/api/files/{file_id}", headers=auth_header)
        assert resp.status_code == 200
        assert resp.get_json()["original_name"] == "file.txt"

    def test_get_nonexistent_file(self, client, auth_header):
        resp = client.get("/api/files/999", headers=auth_header)
        assert resp.status_code == 404

    def test_download_file(self, client, auth_header):
        self._upload(client, auth_header, content=b"download me")
        up = client.get("/api/files", headers=auth_header)
        file_id = up.get_json()[0]["id"]
        resp = client.get(f"/api/files/{file_id}/download", headers=auth_header)
        assert resp.status_code == 200
        assert resp.data == b"download me"

    def test_delete_file(self, client, auth_header):
        up = self._upload(client, auth_header)
        file_id = up.get_json()["uploaded"][0]["id"]
        resp = client.delete(f"/api/files/{file_id}", headers=auth_header)
        assert resp.status_code == 200
        # Confirm it's gone
        resp2 = client.get(f"/api/files/{file_id}", headers=auth_header)
        assert resp2.status_code == 404

    def test_delete_nonexistent(self, client, auth_header):
        resp = client.delete("/api/files/999", headers=auth_header)
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════
#  Health Check
# ═══════════════════════════════════════════════════════════════

class TestHealth:
    def test_health(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "ok"
