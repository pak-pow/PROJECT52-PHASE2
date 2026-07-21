from flask import Flask
from flask_cors import CORS  # type: ignore
from app.config.settings import Config
from app.db import init_db
import os


def create_app(test_config=None):
    """Flask application factory."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    # ── CORS ──────────────────────────────────────────────────
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    # ── Ensure required directories exist ─────────────────────
    os.makedirs(os.path.dirname(app.config["DB_PATH"]),  exist_ok=True)
    os.makedirs(app.config["AVATAR_DIR"],                exist_ok=True)
    os.makedirs(app.config["POST_IMAGE_DIR"],            exist_ok=True)

    # ── Init DB ───────────────────────────────────────────────
    with app.app_context():
        init_db()

    # ── Register Blueprints ───────────────────────────────────
    from app.routes.auth_routes import auth_bp
    from app.routes.post_routes import post_bp
    from app.routes.user_routes import user_bp
    from app.routes.health_routes import health_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(health_bp)

    return app
