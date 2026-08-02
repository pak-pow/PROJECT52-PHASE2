import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("[SERVER] Rate Limiter API server running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
