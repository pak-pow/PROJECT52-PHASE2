from flask import Flask
from flask_cors import CORS  # type: ignore
from app.config.settings import Config
from app.db import close_db, init_db
from app.routes.health_routes import health_bp
from app.routes.auth_routes import auth_bp
from app.routes.service_routes import service_bp
from app.routes.provider_routes import provider_bp
from app.routes.booking_routes import booking_bp


def create_app(config_class=Config):
    """Flask application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for all API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Teardown database connection after request
    app.teardown_appcontext(close_db)

    # Register API blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(service_bp)
    app.register_blueprint(provider_bp)
    app.register_blueprint(booking_bp)

    return app
