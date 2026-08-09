import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "canvas-drawing-secret-key-2026")
    DEFAULT_ROOM_EXPIRY_HOURS = int(os.getenv("DEFAULT_ROOM_EXPIRY_HOURS", "24"))
    MAX_STROKE_HISTORY = int(os.getenv("MAX_STROKE_HISTORY", "5000"))
    CORS_ALLOWED_ORIGINS = "*"
