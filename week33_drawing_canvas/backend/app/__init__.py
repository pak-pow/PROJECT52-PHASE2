from flask import Flask
from flask_socketio import SocketIO
from app.config.settings import Config
from app.routes.health_routes import health_bp
from app.routes.room_routes import room_bp
from app.events.room_events import register_room_events
from app.events.canvas_events import register_canvas_events

socketio = SocketIO(cors_allowed_origins="*")

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for HTTP routes
    @app.after_request
    def apply_cors(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    # Register Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(room_bp)

    # Initialize SocketIO with Flask app
    socketio.init_app(app)

    # Register WebSocket Events
    register_room_events(socketio)
    register_canvas_events(socketio)

    return app
