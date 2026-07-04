import os

class Config: 
    SECRET_KEY = os.environ.get("SECRET_KEY", "week28-quiz-secret-key-change-me")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "data/quiz.db")
    CORS_ORIGIN = os.environ.get("CORS_ORIGIN", "http://localhost:5500")
    DEBUG = os.environ.get("FLASK_ENV", "development") == "development"