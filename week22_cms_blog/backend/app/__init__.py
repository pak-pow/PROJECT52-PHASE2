from flask import Flask #type:ignore
from flask_cors import CORS #type:ignore
from flask_jwt_extended import JWTManager #type:ignore 
from .extensions.db import close_db, init_db
from .api.posts import posts_bp
from .api.auth import auth_bp #type:ignore


def create_app():
    
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('config.Config')

    jwt = JWTManager(app)
    
    init_db(app)
    app.teardown_appcontext(close_db)
    app.register_blueprint(posts_bp, url_prefix='/api/posts')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    @app.route('/api/health')
    def health():
        return {"status": "healthy", "architecture": "Deeply Nested File Structure"}
    
    return app