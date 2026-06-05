from urllib.parse import urlparse
from app.models import url_model
from app.utils.base62 import encode


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_valid_url(url: str) -> bool:
    """Basic URL validation — must have a scheme (http/https) and a netloc."""
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Public Service API
# ---------------------------------------------------------------------------

def shorten_url(original_url: str) -> dict:
    """
    Main business logic for shortening a URL.

    Steps:
      1. Validate the URL.
      2. Check if it's already been shortened (return existing record if so).
      3. Insert a placeholder row to get the auto-increment ID.
      4. Encode that ID with Base62 to produce the short code.
      5. Update the row with the short code and return it.

    Returns:
        The URL record dict: {id, original_url, short_code, clicks, created_at}

    Raises:
        ValueError: If the URL is invalid.
    """
    original_url = original_url.strip()

    if not _is_valid_url(original_url):
        raise ValueError("Invalid URL. Must start with http:// or https://")

    # Return existing record if URL was already shortened
    existing = url_model.find_by_original_url(original_url)
    if existing:
        return existing

    # Insert a temporary placeholder to obtain the auto-increment ID
    from app.utils.db import get_db
    db = get_db()
    cursor = db.execute(
        "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
        (original_url, '__placeholder__')
    )
    db.commit()
    new_id = cursor.lastrowid

    # Encode the ID into a Base62 short code
    short_code = encode(new_id)

    # Update the row with the real short code
    db.execute(
        "UPDATE urls SET short_code = ? WHERE id = ?",
        (short_code, new_id)
    )
    db.commit()

    return url_model.find_by_id(new_id)


def resolve_url(short_code: str) -> dict:
    """
    Look up a short code and increment its click counter.

    Returns:
        The URL record dict.

    Raises:
        KeyError: If the short code doesn't exist.
    """
    record = url_model.find_by_code(short_code)
    if not record:
        raise KeyError(f"Short code '{short_code}' not found.")

    url_model.increment_clicks(short_code)
    return record


def get_stats() -> list[dict]:
    """Return all shortened URLs with their click analytics."""
    return url_model.get_all_urls()
