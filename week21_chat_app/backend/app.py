from flask import Flask #type:ignore
from flask_socketio import SocketIO, send
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'p52_chat_secret'

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('chat_message')
def handle_chat_message(data):
    print(f"Server Received: {data}")
    socketio.emit('chat_message', data)

if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)