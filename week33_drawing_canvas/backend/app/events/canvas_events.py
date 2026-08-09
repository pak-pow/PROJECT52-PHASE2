from flask import request
from flask_socketio import emit
from app.services.room_manager import room_manager

def register_canvas_events(socketio):

    @socketio.on("draw_stroke")
    def handle_draw_stroke(data):
        room_code = data.get("room_code")
        stroke_payload = data.get("stroke")

        if room_code and stroke_payload:
            room_manager.add_stroke(room_code, stroke_payload)
            # Broadcast stroke to all peer clients in the room
            emit("stroke_received", stroke_payload, to=room_code, include_self=False)

    @socketio.on("clear_canvas")
    def handle_clear_canvas(data):
        room_code = data.get("room_code")
        if room_code:
            room_manager.clear_canvas(room_code)
            # Broadcast clear canvas command to all clients in the room
            emit("canvas_cleared", {"room_code": room_code}, to=room_code)
