import os


class Config:
    """Application configuration for Week 31 Booking System."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-week31-booking-key")
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"

    # Rate Limiting & Limits
    MAX_BOOKINGS_PER_DAY_PER_USER = 5

    # Storage Paths
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DB_PATH = os.environ.get(
        "DB_PATH",
        os.path.normpath(os.path.join(_BASE_DIR, "data", "booking.db"))
    )
