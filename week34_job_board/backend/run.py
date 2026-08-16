import os
from app import create_app
from data.seed import seed_database

app = create_app()

if __name__ == "__main__":
    seed_database()
    print("[SERVER] Job Board Platform Backend running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
