import os
from app import create_app
from app.utils.db import init_db

app = create_app()

if __name__ == '__main__':
    # Initialize the database (creates tables if they don't exist yet)
    with app.app_context():
        init_db()

    # FIX: Debug mode is now controlled by the FLASK_DEBUG env var (standard Flask convention).
    # FLASK_DEBUG=1 → debug on (development only).
    # FLASK_DEBUG=0 or unset → debug off (safe for production).
    # Never use FLASK_ENV to infer debug mode.
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug, port=5000)
