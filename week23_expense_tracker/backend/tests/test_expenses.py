import pytest #type: ignore
import os
import tempfile
from app import create_app 
from flask_jwt_extended import create_access_token #type: ignore

@pytest.fixture
def app():
    """Creates a temporary database and test application."""
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE": db_path,
        "JWT_SECRET_KEY": "test-secret-key"
    })

    with app.app_context():
        from app.utils.db import get_db
        db = get_db()
        with open(os.path.join(app.root_path, '..', 'schema.sql'), 'r') as f:
            db.executescript(f.read())
        
        db.execute('INSERT INTO users (id, username, password_hash) VALUES (1, "testadmin", "hash")')
        db.commit()

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Provides a fake browser to make requests."""
    return app.test_client()

@pytest.fixture
def auth_headers(app):
    """Generates a valid JWT token for User ID 1."""
    with app.app_context():
        token = create_access_token(identity="1") 
        return {"Authorization": f"Bearer {token}"}

def test_unauthorized_access(client):
    """Test 1: Ensure the API blocks requests without a JWT token."""
    response = client.get('/api/expenses/')
    assert response.status_code == 401

def test_create_expense(client, auth_headers):
    """Test 2: Ensure we can create an expense securely."""
    data = {
        "amount": 50.50,
        "category": "Food",
        "description": "Test Pizza",
        "date": "2026-06-01"
    }
    response = client.post('/api/expenses/', json=data, headers=auth_headers)
    
    assert response.status_code == 201
    assert "Expense logged successfully" in response.get_json()["message"]
    assert "id" in response.get_json()

def test_get_expenses_and_summary(client, auth_headers):
    """Test 3: Ensure we can fetch raw rows and aggregated math."""
    client.post('/api/expenses/', json={"amount": 10.00, "category": "Food", "date": "2026-06-01"}, headers=auth_headers)
    client.post('/api/expenses/', json={"amount": 20.00, "category": "Food", "date": "2026-06-02"}, headers=auth_headers)
    
    raw_response = client.get('/api/expenses/', headers=auth_headers)
    assert raw_response.status_code == 200
    assert len(raw_response.get_json()) == 2
    
    summary_response = client.get('/api/expenses/summary', headers=auth_headers)
    assert summary_response.status_code == 200
    summary_data = summary_response.get_json()
    assert summary_data[0]["category"] == "Food"
    assert summary_data[0]["total_amount"] == 30.00

def test_delete_expense(client, auth_headers):
    """Test 4: Ensure an expense can be deleted."""
    post_res = client.post('/api/expenses/', json={"amount": 100, "category": "Rent", "date": "2026-06-01"}, headers=auth_headers)
    expense_id = post_res.get_json()["id"]
    
    del_res = client.delete(f'/api/expenses/{expense_id}', headers=auth_headers)
    assert del_res.status_code == 200
    
    get_res = client.get('/api/expenses/', headers=auth_headers)
    assert len(get_res.get_json()) == 0