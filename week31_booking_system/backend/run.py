from app import create_app
from app.db import init_db

app = create_app()

if __name__ == "__main__":
    init_db()
    print("🚀 Week 31 Booking System REST API running on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
