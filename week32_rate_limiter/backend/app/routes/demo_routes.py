import time
from flask import Blueprint, jsonify, request
from app.middleware.limiter import rate_limit

demo_bp = Blueprint("demo", __name__)

@demo_bp.route("/api/public/ping", methods=["GET"])
@rate_limit(limit=10, window=60.0, algorithm="token_bucket")
def public_ping():
    return jsonify({
        "message": "Pong! Public endpoint response.",
        "timestamp": time.time(),
        "limit": "10 reqs / 60 sec (Token Bucket)"
    }), 200

@demo_bp.route("/api/data/burst-test", methods=["GET"])
@rate_limit(limit=5, window=10.0, algorithm="token_bucket")
def burst_test():
    return jsonify({
        "message": "Burst test successful!",
        "timestamp": time.time(),
        "limit": "5 reqs / 10 sec (Token Bucket)"
    }), 200

@demo_bp.route("/api/sliding/test", methods=["GET"])
@rate_limit(limit=5, window=10.0, algorithm="sliding_window")
def sliding_test():
    return jsonify({
        "message": "Sliding window test successful!",
        "timestamp": time.time(),
        "limit": "5 reqs / 10 sec (Sliding Window Log)"
    }), 200

@demo_bp.route("/api/action/heavy", methods=["POST", "GET"])
@rate_limit(limit=2, window=30.0, algorithm="token_bucket")
def heavy_action():
    return jsonify({
        "message": "Heavy action executed successfully!",
        "timestamp": time.time(),
        "limit": "2 reqs / 30 sec (Strict Action Limit)"
    }), 200
