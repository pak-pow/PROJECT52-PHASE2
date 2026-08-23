from flask import Flask
from flask_cors import CORS
from app.config.settings import Config
from app.db import init_db
from app.routes.health_routes import health_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register Blueprints
    app.register_blueprint(health_bp)

    # Initialize Database Schema
    with app.app_context():
        init_db()

    return app
