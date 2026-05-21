from flask import Flask, request #type:ignore
from flask_socketio import SocketIO, emit, join_room, leave_room #type: ignore
from flask_cors import CORS #type: ignore

app = Flask(__name__)
app.config['SECRET_KEY'] = 'p52_chat_secret'

socketio = SocketIO(app, cors_allowed_origins="*")

active_users = {}

@socketio.on('user_join')
def handle_user_join(data):
    username = data['username']
    room = data['room']

    active_users[request.sid] = {'username': username, "room": room}
    join_room(room)

    emit('system_message', f"{username} joined the {room} room", to=room)

@socketio.on('chat_message')
def handle_chat_message(data):
    socketio.emit('chat_message', data)
    
@socketio.on('typing')
def handle_typing(data):
    emit('typing', data, broadcast=True, include_self=False)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in active_users:
        username = active_users.pop(request.sid)
        emit('system_message', f"{username} left the chat", broadcast=True)

if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)