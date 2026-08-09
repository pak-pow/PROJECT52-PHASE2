from flask import request
from flask_socketio import emit, join_room, leave_room
from app.services.room_manager import room_manager

def register_room_events(socketio):

    @socketio.on("join_room")
    def handle_join_room(data):
        sid = request.sid
        room_code = data.get("room_code", "").upper().strip()
        username = data.get("username", "Anonymous Artist").strip()

        if not room_code:
            emit("error", {"message": "Room code is required."})
            return

        join_room(room_code)
        session_info = room_manager.join_room(room_code, sid, username)

        # Notify user with full room state & stroke history for late joiners
        emit("room_joined", {
            "room_code": session_info["room_code"],
            "user": session_info["user"],
            "users_list": session_info["users_list"],
            "strokes_history": session_info["strokes_history"]
        })

        # Broadcast user joined event to room peers
        emit("user_joined", {
            "user": session_info["user"],
            "users_list": session_info["users_list"]
        }, to=room_code, include_self=False)

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        room_code, left_info = room_manager.leave_room(sid)
        if room_code and left_info:
            leave_room(room_code)
            emit("user_left", {
                "user": left_info["user"],
                "users_list": left_info["remaining_users"]
            }, to=room_code)

    @socketio.on("cursor_move")
    def handle_cursor_move(data):
        sid = request.sid
        room_code = data.get("room_code")
        if room_code:
            emit("cursor_update", {
                "sid": sid,
                "username": data.get("username", "Artist"),
                "color": data.get("color", "#3b82f6"),
                "x": data.get("x"),
                "y": data.get("y")
            }, to=room_code, include_self=False)
