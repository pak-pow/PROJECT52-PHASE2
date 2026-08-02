import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "rate-limiter-secret-key-2026")
    DEFAULT_RATE_LIMIT = int(os.getenv("DEFAULT_RATE_LIMIT", "10"))  # 10 requests
    DEFAULT_WINDOW_SECONDS = int(os.getenv("DEFAULT_WINDOW_SECONDS", "60"))  # per 60 seconds
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    STORAGE_TYPE = os.getenv("STORAGE_TYPE", "memory")  # 'memory' or 'redis'
