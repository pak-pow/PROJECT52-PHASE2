import os 
from flask import Flask # type: ignore
from flask_cors import CORS # type: ignore

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")
MAX_CONTENT_LENGTH = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS 

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    with app.app_context():
        from app.utils.db import init_db
        init_db()

        from app.routes.recipe_routes import recipe_bp
        app.register_blueprint(recipe_bp)
    
    return app