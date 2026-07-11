"""
WSGI Entrypoint for serving the Quiz Platform backend in production.

To run:
    python wsgi.py
"""

import sys
import os

# Add backend directory to path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from waitress import serve  # type: ignore

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Serving production Flask app on http://0.0.0.0:{port} via Waitress...")
    serve(app, host="0.0.0.0", port=port)
