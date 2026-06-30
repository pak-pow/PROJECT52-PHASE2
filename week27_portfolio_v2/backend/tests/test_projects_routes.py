"""
Tests for /api/projects endpoints
"""


class TestListProjects:

    def test_get_projects_returns_200(self, client):
        res = client.get("/api/projects")
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_get_projects_returns_seeded_data(self, client):
        res = client.get("/api/projects")
        data = res.get_json()
        assert len(data) >= 4  # 4 seeded projects
        titles = [p["title"] for p in data]
        assert "PROJECT_PYGAME" in titles

    def test_projects_have_required_fields(self, client):
        res = client.get("/api/projects")
        project = res.get_json()[0]
        for field in ["id", "title", "description", "tech_stack", "status", "featured"]:
            assert field in project


class TestCreateProject:

    def test_create_without_auth_returns_401(self, client):
        res = client.post("/api/projects", json={
            "title": "Test", "description": "Desc", "tech_stack": "Python"
        })
        assert res.status_code == 401

    def test_create_with_auth_returns_201(self, client, auth_headers):
        res = client.post("/api/projects", json={
            "title":       "New Project",
            "description": "A test project",
            "tech_stack":  "Python, Flask",
            "status":      "In Progress",
        }, headers=auth_headers)
        assert res.status_code == 201
        assert res.get_json()["title"] == "New Project"

    def test_create_missing_title_returns_400(self, client, auth_headers):
        res = client.post("/api/projects", json={
            "description": "Desc", "tech_stack": "Python"
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_create_missing_description_returns_400(self, client, auth_headers):
        res = client.post("/api/projects", json={
            "title": "Test", "tech_stack": "Python"
        }, headers=auth_headers)
        assert res.status_code == 400
        
    def test_create_featured_project_returns_201(self, client, auth_headers):
        res = client.post("/api/projects", json={
            "title":       "Featured Project",
            "description": "A very special test project",
            "tech_stack":  "OpenGL, C++",
            "status":      "Completed",
            "featured":    True
        }, headers=auth_headers)
        assert res.status_code == 201
        data = res.get_json()
        assert data["title"] == "Featured Project"
        assert data["featured"] == 1

class TestUpdateProject:

    def test_update_without_auth_returns_401(self, client):
        res = client.put("/api/projects/1", json={"title": "Updated"})
        assert res.status_code == 401

    def test_update_with_auth_returns_200(self, client, auth_headers):
        res = client.put("/api/projects/1", json={
            "title": "Updated Title"
        }, headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["title"] == "Updated Title"

    def test_update_nonexistent_returns_404(self, client, auth_headers):
        res = client.put("/api/projects/99999", json={
            "title": "Ghost"
        }, headers=auth_headers)
        assert res.status_code == 404
        
    def test_update_featured_status_returns_200(self, client, auth_headers):
        res = client.put("/api/projects/2", json={
            "featured": True
        }, headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["featured"] == 1

        res2 = client.put("/api/projects/2", json={
            "featured": False
        }, headers=auth_headers)
        assert res2.status_code == 200
        assert res2.get_json()["featured"] == 0


class TestDeleteProject:

    def test_delete_without_auth_returns_401(self, client):
        res = client.delete("/api/projects/1")
        assert res.status_code == 401

    def test_delete_with_auth_returns_204(self, client, auth_headers):
        res = client.delete("/api/projects/1", headers=auth_headers)
        assert res.status_code == 204

    def test_delete_nonexistent_returns_404(self, client, auth_headers):
        res = client.delete("/api/projects/99999", headers=auth_headers)
        assert res.status_code == 404


class TestReorderProject:

    def test_reorder_without_auth_returns_401(self, client):
        res = client.post("/api/projects/1/reorder", json={"direction": "up"})
        assert res.status_code == 401

    def test_reorder_invalid_direction_returns_400(self, client, auth_headers):
        res = client.post(
            "/api/projects/1/reorder",
            headers=auth_headers,
            json={"direction": "invalid"},
        )
        assert res.status_code == 400

    def test_reorder_nonexistent_returns_404(self, client, auth_headers):
        res = client.post(
            "/api/projects/99999/reorder",
            headers=auth_headers,
            json={"direction": "up"},
        )
        assert res.status_code == 404

    def test_reorder_swaps_sort_orders_returns_200(self, client, auth_headers):
        res1 = client.post(
            "/api/projects",
            headers=auth_headers,
            json={
                "title": "First",
                "description": "Desc",
                "tech_stack": "Tech",
                "sort_order": 10,
            },
        )
        p1 = res1.get_json()

        res2 = client.post(
            "/api/projects",
            headers=auth_headers,
            json={
                "title": "Second",
                "description": "Desc",
                "tech_stack": "Tech",
                "sort_order": 20,
            },
        )
        p2 = res2.get_json()

        # Swap Second "up"
        res_swap = client.post(
            f"/api/projects/{p2['id']}/reorder",
            headers=auth_headers,
            json={"direction": "up"},
        )
        assert res_swap.status_code == 200

        # Fetch projects to verify order swapped
        res_list = client.get("/api/projects")
        projects = res_list.get_json()
        
        p1_new = next(p for p in projects if p["id"] == p1["id"])
        p2_new = next(p for p in projects if p["id"] == p2["id"])

        assert p1_new["sort_order"] == 20
        assert p2_new["sort_order"] == 10
