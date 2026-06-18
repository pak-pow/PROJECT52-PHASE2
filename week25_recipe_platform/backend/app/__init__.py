import os
from flask import Flask  # type: ignore
from flask_cors import CORS  # type: ignore

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")
MAX_CONTENT_LENGTH = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# Origins allowed to call the API. Extend this list for staging/production.
ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    # file:// origin used when opening index.html directly in the browser
    "null",
]


def create_app():
    app = Flask(__name__)
    CORS(app, origins=ALLOWED_ORIGINS)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    with app.app_context():
        from app.utils.db import init_db, close_db
        init_db()

        # Ensure DB connections are closed after every request
        app.teardown_appcontext(close_db)

        from app.routes.recipe_routes import recipe_bp
        app.register_blueprint(recipe_bp)

    return app