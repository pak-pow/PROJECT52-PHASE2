from flask import Flask, jsonify #type: ignore
from flask_cors import CORS #type: ignore
from app.config.settings import Config
from app.db import init_db
from app.routes.quiz_routes import quiz_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "null",  # file:// protocol (opening index.html directly)
    ]}})
    
    with app.app_context():
        init_db()

    # Register blueprints
    app.register_blueprint(quiz_bp)
        
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "project": "week28_quiz_platform"}), 200
    
    return app