"""
settings.py
Centralised application configuration constants.
Import from here instead of scattering magic values across files.
"""

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    # "null" covers opening HTML files directly in the browser via file://
    "null",
]

# ---------------------------------------------------------------------------
# File uploads
# ---------------------------------------------------------------------------
MAX_CONTENT_LENGTH = 5 * 1024 * 1024          # 5 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
SEND_FILE_MAX_AGE  = 31_536_000               # 1 year in seconds

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------
DEFAULT_PER_PAGE = 12
MAX_PER_PAGE     = 100

# ---------------------------------------------------------------------------
# Recipe categories
# ---------------------------------------------------------------------------
CATEGORIES = [
    'Breakfast',
    'Lunch',
    'Dinner',
    'Dessert',
    'Snacks',
    'Soup',
    'Uncategorised',
]
