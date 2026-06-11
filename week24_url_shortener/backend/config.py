import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable is not set. Check your .env file.")

    # FIX: FLASK_ENV is deprecated in Flask 2.3+. Never rely on it to toggle debug mode.
    # debug is controlled explicitly in run.py via FLASK_DEBUG env var.

    # FIX: BASE_URL is used when building short URLs in responses.
    # Hardcoding this prevents Host Header Injection attacks where an attacker
    # manipulates the Host header to make the server return a deceptive short_url.
    BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:5000')

    # FIX: Load CORS allowed origins from env so we don't need code changes for production.
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://127.0.0.1:5500,http://localhost:5500').split(',')
