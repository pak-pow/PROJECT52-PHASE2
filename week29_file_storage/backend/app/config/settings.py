import os


class Config:
    """Application configuration — reads from env vars with sensible defaults."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"

    # ── File Upload Limits ────────────────────────────────────
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10 MB
    MAX_FILES_PER_REQUEST = 10

    # ── Allowed MIME Types ────────────────────────────────────
    ALLOWED_MIME_TYPES = {
        # Images
        "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml",
        # Documents
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain", "text/csv", "text/markdown",
        # Audio
        "audio/mpeg", "audio/wav", "audio/ogg",
        # Video
        "video/mp4", "video/webm",
        # Archives
        "application/zip", "application/x-tar", "application/gzip",
    }

    # ── Storage Paths ─────────────────────────────────────────
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR = os.environ.get(
        "UPLOAD_DIR",
        os.path.normpath(os.path.join(_BASE_DIR, "uploads"))
    )
    THUMBNAIL_DIR = os.environ.get(
        "THUMBNAIL_DIR",
        os.path.normpath(os.path.join(_BASE_DIR, "thumbnails"))
    )

    # ── Thumbnail Settings ────────────────────────────────────
    THUMBNAIL_SIZE = (200, 200)

    # ── Category Mapping ──────────────────────────────────────
    @staticmethod
    def get_category(mime_type: str) -> str:
        """Derive a human-friendly category from MIME type."""
        if mime_type.startswith("image/"):
            return "image"
        if mime_type.startswith("audio/"):
            return "audio"
        if mime_type.startswith("video/"):
            return "video"
        if mime_type in (
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain", "text/csv", "text/markdown",
        ):
            return "document"
        return "other"
