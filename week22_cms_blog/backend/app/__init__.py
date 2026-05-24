from flask import Flask #type:ignore
from .extensions.db import close_db, init_db
from .api.posts import posts_bp

def create_app():
    
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    init_db(app)
    app.teardown_appcontext(close_db)
    
    app.register_blueprint(posts_bp, url_prefix='/api/posts')
    
    @app.route('/api/health')
    def health():
        return {"status": "healthy", "architecture": "Deeply Nested File Structure"}
    
    return app