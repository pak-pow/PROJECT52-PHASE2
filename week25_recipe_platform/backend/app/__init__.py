import os
import logging
from flask import Flask  # type: ignore
from flask_cors import CORS  # type: ignore
from app.config.settings import (
    ALLOWED_ORIGINS,
    ALLOWED_EXTENSIONS,
    MAX_CONTENT_LENGTH,
    SEND_FILE_MAX_AGE,
)

BASE_DIR     = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")


def create_app():
    app = Flask(__name__)
    CORS(app, origins=ALLOWED_ORIGINS)

    # --- Flask config (sourced from settings.py) ---
    app.config['UPLOAD_FOLDER']          = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH']     = MAX_CONTENT_LENGTH
    app.config['ALLOWED_EXTENSIONS']     = ALLOWED_EXTENSIONS
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = SEND_FILE_MAX_AGE

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # --- Request logger middleware ---
    logging.basicConfig(level=logging.INFO)
    from app.middlewares.request_logger import register_logger
    register_logger(app)

    with app.app_context():
        from app.utils.db import init_db, close_db
        init_db()

        # Close DB connections after every request
        app.teardown_appcontext(close_db)

        from app.routes.recipe_routes import recipe_bp
        app.register_blueprint(recipe_bp)

    return app