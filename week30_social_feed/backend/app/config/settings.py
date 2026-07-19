import os


class Config:
    """Application configuration — reads from env vars with sensible defaults."""

    # ── Security ──────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production-immediately")
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"

    # ── Rate Limiting (simple per-user) ───────────────────────
    MAX_POSTS_PER_MINUTE = 10

    # ── File Upload Limits ────────────────────────────────────
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_FILE_SIZE", 5 * 1024 * 1024))  # 5 MB
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

    # ── Image Processing ──────────────────────────────────────
    AVATAR_SIZE = (200, 200)
    POST_IMAGE_MAX_SIZE = (1200, 900)
    IMAGE_QUALITY = 85

    # ── Storage Paths ─────────────────────────────────────────
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR = os.environ.get(
        "UPLOAD_DIR",
        os.path.normpath(os.path.join(_BASE_DIR, "uploads"))
    )
    AVATAR_DIR = os.environ.get(
        "AVATAR_DIR",
        os.path.normpath(os.path.join(_BASE_DIR, "uploads", "avatars"))
    )
    POST_IMAGE_DIR = os.environ.get(
        "POST_IMAGE_DIR",
        os.path.normpath(os.path.join(_BASE_DIR, "uploads", "posts"))
    )
    DB_PATH = os.environ.get(
        "DB_PATH",
        os.path.normpath(os.path.join(_BASE_DIR, "data", "social.db"))
    )

    # ── Pagination ────────────────────────────────────────────
    FEED_PAGE_SIZE = 20
    EXPLORE_PAGE_SIZE = 20

    # ── Validation ────────────────────────────────────────────
    MIN_USERNAME_LEN = 3
    MAX_USERNAME_LEN = 30
    MIN_PASSWORD_LEN = 6
    MAX_POST_LEN = 280
    MAX_BIO_LEN = 160
    MAX_DISPLAY_NAME_LEN = 50
