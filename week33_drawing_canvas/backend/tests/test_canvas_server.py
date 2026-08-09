import os
import sys
import pytest

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, socketio
from app.services.room_manager import room_manager

@pytest.fixture
def app_instance():
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

def test_health_check_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "week33_drawing_canvas"

def test_create_and_get_room(client):
    res = client.post("/api/rooms", json={"room_code": "TEST-ROOM-1"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["room_code"] == "TEST-ROOM-1"

    details_res = client.get("/api/rooms/TEST-ROOM-1")
    assert details_res.status_code == 200
    details = details_res.get_json()
    assert details["room_code"] == "TEST-ROOM-1"
    assert details["user_count"] == 0

def test_room_manager_unit():
    code = room_manager.create_room("UNIT-ROOM")
    assert code == "UNIT-ROOM"

    join_res = room_manager.join_room("UNIT-ROOM", sid="sid-101", username="Vee")
    assert join_res["user"]["username"] == "Vee"
    assert len(join_res["users_list"]) == 1

    room_manager.add_stroke("UNIT-ROOM", {"type": "path", "points": [10, 10, 20, 20]})
    details = room_manager.get_room_details("UNIT-ROOM")
    assert details["stroke_count"] == 1

    room_manager.clear_canvas("UNIT-ROOM")
    details_cleared = room_manager.get_room_details("UNIT-ROOM")
    assert details_cleared["stroke_count"] == 0

    room_code, left_info = room_manager.leave_room("sid-101")
    assert room_code == "UNIT-ROOM"
    assert left_info["user"]["username"] == "Vee"
