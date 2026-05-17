from flask import Flask #type:ignore
from flask_socketio import SocketIO, send
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'p52_chat_secret'

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('message')
def handle_message(msg):
    print(f"Server Received: {msg}")
    send(msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, port=5000, debug=True)