from flask import Flask
from flask_cors import CORS
from config import Config
from app.utils.db import close_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=["http://127.0.0.1:5500", "http://localhost:5500"])

    app.teardown_appcontext(close_db)

    # Security headers on every response
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    # Register blueprints
    from app.routes.url_routes import url_bp
    app.register_blueprint(url_bp)

    return app
