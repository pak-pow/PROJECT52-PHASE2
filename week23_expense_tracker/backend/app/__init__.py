from flask import Flask #type: ignore
from flask_cors import CORS #type: ignore
from config import Config #type: ignore
from .utils.db import close_db
from .routes.expenses import expenses_bp
from .routes.auth import auth_bp 
from flask_jwt_extended import JWTManager #type: ignore

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://127.0.0.1:5500", "http://localhost:5500"])
    
    app.config.from_object(Config)
    jwt = JWTManager(app)
    
    from .extensions import limiter
    limiter.init_app(app)
    
    app.teardown_appcontext(close_db)
    app.register_blueprint(expenses_bp, url_prefix='/api/expenses')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    @app.route('/api/health')
    def health_check():
        return {"status": "healthy", "service": "Expense Tracker API"}
        
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'no-referrer'
        return response

    return app