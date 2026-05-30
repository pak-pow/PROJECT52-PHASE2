import pytest # type: ignore
import json
from app import create_app
from app.extensions.db import get_db
from werkzeug.security import generate_password_hash # type: ignore
import tempfile
import os
@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE": db_path, 
        "JWT_SECRET_KEY": "test-secret-key"
    })

    with app.app_context():
        db = get_db()
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
            
        db.execute("UPDATE users SET password_hash = ? WHERE username = ?", 
            (generate_password_hash('admin123'), 'admin'))
        db.commit()
        db.commit()

    yield app
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()


def test_public_get_posts(client):
    """Test that anyone can read the blog feed."""
    response = client.get('/api/posts/')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_protected_route_without_token_fails(client):
    """Test that the API bounces unauthorized POST requests."""
    response = client.post('/api/posts/', json={
        "title": "Hacker Post",
        "content": "Trying to bypass security!"
    })
    assert response.status_code == 401 

def test_login_success_returns_token(client):
    """Test that valid credentials return a 200 OK and a JWT."""
    response = client.post('/api/auth/login', json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "token" in response.json

def test_protected_route_with_token_succeeds(client):
    """Test the full flow: Login, get token, and create a post."""
    # 1. Login
    login_res = client.post('/api/auth/login', json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_res.json['token']

    response = client.post('/api/posts/', 
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Automated Test Post",
            "content": "This was created by Pytest!"
        }
    )
    
    print("Response JSON:", response.json)
    assert response.status_code == 201
    assert response.json['message'] == "Post created successfully!"