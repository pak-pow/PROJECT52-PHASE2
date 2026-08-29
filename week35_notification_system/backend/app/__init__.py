from flask import Flask
from flask_cors import CORS
from app.config.settings import Config
from app.db import init_db
from data.seed import seed_database
from app.routes.health_routes import health_bp
from app.routes.notification_routes import notification_bp
from app.routes.preference_routes import preference_bp
from app.routes.template_routes import template_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(preference_bp)
    app.register_blueprint(template_bp)

    # Initialize Database Schema & Seed Data
    with app.app_context():
        init_db()
        seed_database()

    return app
