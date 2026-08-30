import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from data.seed import seed_database
from app.models.event_model import EventModel

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # Auto-seed database on first startup if events table is empty
        if EventModel.get_total_count() == 0:
            seed_database(1000)

    port = int(os.getenv("PORT", 5000))
    print(f"[SERVER] Week 36 Analytics Dashboard Backend running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
