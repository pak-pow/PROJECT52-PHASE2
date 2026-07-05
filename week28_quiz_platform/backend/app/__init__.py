from flask import Flask, jsonify #type: ignore
from flask_cors import CORS #type: ignore
from app.config.settings import Config
from app.db import init_db
from app.routes.quiz_routes import quiz_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGIN}})
    
    with app.app_context():
        init_db()

    # Register blueprints
    app.register_blueprint(quiz_bp)
        
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "project": "week28_quiz_platform"}), 200
    
    return app