"""
Week 27: Portfolio v2 — Flask Application Factory
"""

from flask import Flask
from flask_cors import CORS

from config import Config
from app.db import init_app as init_db_app, init_db
from app.routes.contact_routes import contact_bp
from app.routes.projects_routes import projects_bp
from app.routes.admin_routes import admin_bp



def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for frontend dev server
    CORS(app, origins=app.config["CORS_ORIGINS"])

    # Register database lifecycle helpers
    init_db_app(app)

    # Register API blueprints under /api prefix
    app.register_blueprint(contact_bp, url_prefix="/api")
    app.register_blueprint(projects_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api")

    # Auto-init DB only when not in test mode
    # (Tests call init_db() themselves inside their fixture)
    if not app.config.get("TESTING"):
        with app.app_context():
            init_db()

    @app.route("/api/health")
    def health():
        return {"status": "ok", "project": "portfolio-v2"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
