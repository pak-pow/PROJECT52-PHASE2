import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    print("[SERVER] Multi-User Drawing Canvas WebSocket Server running at http://127.0.0.1:5000")
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
