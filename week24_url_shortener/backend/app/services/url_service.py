from urllib.parse import urlparse
from app.models import url_model
from app.utils.base62 import encode
from datetime import datetime, timedelta, timezone 
import re

class AliasTakenError(Exception):
    pass

class ExpiredURLError(Exception):
    pass

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def is_valid_url(url: str) -> bool:
    """Basic URL validation — must have a scheme (http/https) and a netloc."""
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False

def is_valid_alias(alias: str) -> bool:
    """Ensure the custom alias is safe (alphanumeric and hyphens, 3-20 chars)."""
    return bool(re.match(r'^[a-zA-Z0-9-]{3,20}$', alias))


# ---------------------------------------------------------------------------
# Public Service API
# ---------------------------------------------------------------------------

def shorten_url(original_url: str, custom_alias: str = None, expires_in_hours: int = None) -> dict: # type: ignore
    if not original_url:
        raise ValueError("URL cannot be empty.")
    if not is_valid_url(original_url):
        raise ValueError("Invalid URL format. Must include http:// or https://")

    expires_at = None
    if expires_in_hours:
        death_clock = datetime.now(timezone.utc) + timedelta(hours = expires_in_hours)
        expires_at = death_clock.isoformat()

    # --- PATH A: CUSTOM ALIAS ---
    if custom_alias:
        if not is_valid_alias(custom_alias):
            raise ValueError("Alias must be 3-20 characters, letters, numbers, or hyphens.")
        
        # Check for collision
        existing_alias = url_model.find_by_code(custom_alias)
        if existing_alias:
            raise AliasTakenError("That custom alias is already taken.") 
        
        return url_model.insert_url(original_url, custom_alias, expires_at) # type: ignore

    # --- PATH B: STANDARD BASE62 ENCODING ---
    existing_entry = url_model.find_by_original_url(original_url)
    if existing_entry:
        return existing_entry

    record = url_model.insert_url(original_url, "PENDING", expires_at) # type: ignore
    short_code = encode(record['id'])
    url_model.update_short_code(record['id'], short_code)
    
    return url_model.find_by_id(record['id']) # type: ignore


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

    if record['expires_at']:
        expiration_date = datetime.fromisoformat(record['expires_at'])
        
        if expiration_date.tzinfo is None:
            expiration_date = expiration_date.replace(tzinfo=timezone.utc)
            
        if datetime.now(timezone.utc) > expiration_date:
            raise ExpiredURLError("This link has self-destructed.")

    url_model.increment_clicks(short_code)
    return record


def get_stats() -> list[dict]:
    """Return all shortened URLs with their click analytics."""
    return url_model.get_all_urls()
