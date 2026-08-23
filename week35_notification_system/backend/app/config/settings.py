import os

class Config:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "data", "notifications.db"))
    SCHEMA_PATH = os.getenv("SCHEMA_PATH", os.path.join(BASE_DIR, "data", "schema.sql"))
    SECRET_KEY = os.getenv("SECRET_KEY", "notification-system-secret-key-2026")

    # Mock Provider Credentials & Configs
    MOCK_SMTP_ENABLED = True
    MOCK_TWILIO_ENABLED = True
    MOCK_WEBHOOK_ENABLED = True
    MAX_RETRY_ATTEMPTS = 3
    RATE_LIMIT_PER_MINUTE = 10
