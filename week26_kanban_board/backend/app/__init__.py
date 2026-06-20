import logging
from flask import Flask  # type: ignore
from flask_cors import CORS  # type: ignore
from app.config import settings
from app.utils.db import init_db, close_db
from app.middlewares.request_logger import register_logger
from app.routes.board_routes import board_bp
from app.routes.column_routes import column_bp
from app.routes.card_routes import card_bp


def create_app():
    app = Flask(__name__)
    CORS(app, origins=settings.ALLOWED_ORIGINS)

    # Enable request logging
    logging.basicConfig(level=logging.INFO)
    register_logger(app)

    with app.app_context():
        init_db()
        app.register_blueprint(board_bp)
        app.register_blueprint(column_bp)
        app.register_blueprint(card_bp)

    app.teardown_appcontext(close_db)
    return app