from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # We will load config and initialize DB here soon
    
    @app.route('/api/health')
    def health_check():
        return {"status": "healthy", "service": "Expense Tracker API"}
        
    return app
