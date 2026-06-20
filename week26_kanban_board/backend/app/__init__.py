from flask import Flask #type: ignore
from flask_cors import CORS #type: ignore
from app.config import settings
from app.utils.db import init_db, close_db

def create_app():
    
    app = Flask(__name__)
    CORS(app, origins=settings.ALLOWED_ORIGINS)
    
    with app.app_context():
        init_db()
        
    app.teardown_appcontext(close_db)
    return app