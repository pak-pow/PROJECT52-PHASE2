import os
from werkzeug.security import generate_password_hash

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask secret key — override via environment variable in production
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")

    # SQLite database path
    DATABASE = os.path.join(basedir, "data", "portfolio.db")

    # Admin credentials — override via environment variables
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    ADMIN_PASSWORD_HASH = os.getenv(
        "ADMIN_PASSWORD_HASH",
        generate_password_hash(ADMIN_PASSWORD)
    )

    # CORS allowed origins (frontend dev server)
    CORS_ORIGINS = ["http://localhost:5500", "http://127.0.0.1:5500",
                    "http://localhost:5000", "http://127.0.0.1:5000"]
