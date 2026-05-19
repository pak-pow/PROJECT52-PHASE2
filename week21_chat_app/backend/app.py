from flask import Flask #type:ignore
from flask_socketio import SocketIO, emit #type: ignore
from flask_cors import CORS #type: ignore

app = Flask(__name__)
app.config['SECRET_KEY'] = 'p52_chat_secret'

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('chat_message')
def handle_chat_message(data):
    print(f"Server Received: {data}")
    socketio.emit('chat_message', data)
    
@socketio.on('typing')
def handle_typing(data):
    emit('typing', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)