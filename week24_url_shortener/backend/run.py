import os
from app import create_app
from app.utils.db import init_db

app = create_app()

if __name__ == '__main__':
    # Initialize the database (creates tables if they don't exist yet)
    with app.app_context():
        init_db()

    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, port=5000)
