from flask import Flask #type: ignore
from flask_cors import CORS #type: ignore
from flask_limiter import Limiter #type: ignore
from flask_limiter.util import get_remote_address #type: ignore
from config import Config
from app.utils.db import close_db

limiter = Limiter(
    key_func = get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri = "memory://"
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=["http://127.0.0.1:5500", "http://localhost:5500"])
    
    limiter.init_app(app)
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
