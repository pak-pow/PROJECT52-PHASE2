import os
from flask import Flask, jsonify  # type: ignore
from flask_cors import CORS  # type: ignore
from app.config.settings import Config
from app.db import init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "null",  # file:// protocol
    ]}})

    # Ensure upload and thumbnail directories exist
    os.makedirs(app.config.get("UPLOAD_DIR", "uploads"), exist_ok=True)
    os.makedirs(app.config.get("THUMBNAIL_DIR", "thumbnails"), exist_ok=True)

    with app.app_context():
        init_db()

    # Register blueprints
    from app.routes.file_routes import file_bp
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(file_bp)
    app.register_blueprint(auth_bp)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "project": "week29_file_storage"}), 200

    return app
