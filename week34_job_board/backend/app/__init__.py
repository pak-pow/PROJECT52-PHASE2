from flask import Flask
from flask_cors import CORS
from app.config.settings import Config
from app.db import init_db
from app.routes.health_routes import health_bp
from app.routes.auth_routes import auth_bp
from app.routes.job_routes import job_bp
from app.routes.application_routes import application_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}, r"/uploads/*": {"origins": "*"}})

    # Register Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(application_bp)

    # Initialize Database Schema
    with app.app_context():
        init_db()

    return app
