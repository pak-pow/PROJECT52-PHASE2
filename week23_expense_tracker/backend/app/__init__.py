from flask import Flask #type: ignore
from flask_cors import CORS #type: ignore
from config import Config #type: ignore
from .utils.db import close_db
from .routes.expenses import expenses_bp 
from flask_jwt_extended import JWTManager #type: ignore

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.config.from_object(Config)
    jwt = JWTManager(app)
    
    app.teardown_appcontext(close_db)
    app.register_blueprint(expenses_bp, url_prefix='/api/expenses')
    
    @app.route('/api/health')
    def health_check():
        return {"status": "healthy", "service": "Expense Tracker API"}
        
    return app