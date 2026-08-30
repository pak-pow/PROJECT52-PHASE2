import os

class Config:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "data", "analytics.db"))
    SCHEMA_PATH = os.getenv("SCHEMA_PATH", os.path.join(BASE_DIR, "data", "schema.sql"))
    SECRET_KEY = os.getenv("SECRET_KEY", "analytics-dashboard-secret-key-2026")

    # Seed Configs
    DEFAULT_SEED_EVENTS_COUNT = 1000
