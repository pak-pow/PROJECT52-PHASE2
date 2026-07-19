"""Tests for post routes: create, feed, explore, delete, like."""


def _register(client, username="poster", password="pass123"):
    resp = client.post("/api/auth/register", json={
        "username": username,
        "display_name": username.capitalize(),
        "password": password,
    })
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_post(client):
    headers = _register(client)
    resp = client.post("/api/posts", data={"content": "Hello world!"}, headers=headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["content"] == "Hello world!"
    assert data["username"] == "poster"


def test_create_post_too_long(client):
    headers = _register(client)
    resp = client.post("/api/posts", data={"content": "x" * 281}, headers=headers)
    assert resp.status_code == 400


def test_create_empty_post(client):
    headers = _register(client)
    resp = client.post("/api/posts", data={"content": ""}, headers=headers)
    assert resp.status_code == 400


def test_home_feed_returns_own_posts(client):
    headers = _register(client)
    client.post("/api/posts", data={"content": "My first post"}, headers=headers)
    resp = client.get("/api/posts", headers=headers)
    assert resp.status_code == 200
    posts = resp.get_json()
    assert any(p["content"] == "My first post" for p in posts)


def test_explore_feed(client):
    headers = _register(client)
    client.post("/api/posts", data={"content": "Explore me!"}, headers=headers)
    resp = client.get("/api/posts/explore", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_delete_own_post(client):
    headers = _register(client)
    create_resp = client.post("/api/posts", data={"content": "To delete"}, headers=headers)
    post_id = create_resp.get_json()["id"]
    del_resp = client.delete(f"/api/posts/{post_id}", headers=headers)
    assert del_resp.status_code == 200


def test_delete_other_user_post_denied(client):
    h1 = _register(client, "owner")
    h2 = _register(client, "attacker")
    create_resp = client.post("/api/posts", data={"content": "Owner's post"}, headers=h1)
    post_id = create_resp.get_json()["id"]
    del_resp = client.delete(f"/api/posts/{post_id}", headers=h2)
    assert del_resp.status_code == 404


def test_like_toggle(client):
    headers = _register(client)
    create_resp = client.post("/api/posts", data={"content": "Like me!"}, headers=headers)
    post_id = create_resp.get_json()["id"]

    like_resp = client.post(f"/api/posts/{post_id}/like", headers=headers)
    assert like_resp.status_code == 200
    assert like_resp.get_json()["liked"] is True

    unlike_resp = client.post(f"/api/posts/{post_id}/like", headers=headers)
    assert unlike_resp.get_json()["liked"] is False


def test_get_post_with_replies(client):
    headers = _register(client)
    post_resp = client.post("/api/posts", data={"content": "Parent post"}, headers=headers)
    post_id = post_resp.get_json()["id"]
    client.post("/api/posts", data={"content": "A reply", "reply_to_id": post_id}, headers=headers)

    get_resp = client.get(f"/api/posts/{post_id}", headers=headers)
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert data["post"]["id"] == post_id
    assert len(data["replies"]) == 1
