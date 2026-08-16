import os

class Config:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "data", "job_board.db"))
    SCHEMA_PATH = os.getenv("SCHEMA_PATH", os.path.join(BASE_DIR, "data", "schema.sql"))
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(BASE_DIR, "uploads"))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    SECRET_KEY = os.getenv("SECRET_KEY", "job-board-secret-key-2026")
