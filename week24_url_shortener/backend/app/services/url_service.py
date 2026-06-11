from urllib.parse import urlparse
from app.models import url_model
from app.utils.base62 import encode
from datetime import datetime, timedelta, timezone
import re


# ---------------------------------------------------------------------------
# Custom domain exceptions — never hijack built-in exceptions for business logic
# ---------------------------------------------------------------------------

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

def shorten_url(original_url: str, custom_alias: str = None, expires_in_hours: int = None) -> dict:  # type: ignore
    # FIX: Type-check inputs before using them — prevents 500 TypeError crashes
    if not isinstance(original_url, str) or not original_url.strip():
        raise ValueError("URL cannot be empty.")
    original_url = original_url.strip()
    if not is_valid_url(original_url):
        raise ValueError("Invalid URL format. Must include http:// or https://")

    if custom_alias is not None and not isinstance(custom_alias, str):
        raise ValueError("custom_alias must be a string.")

    expires_at = None
    if expires_in_hours is not None:
        if not isinstance(expires_in_hours, (int, float)) or isinstance(expires_in_hours, bool):
            raise ValueError("expires_in_hours must be a number.")
        if expires_in_hours <= 0 or expires_in_hours > 8760:  # max 1 year
            raise ValueError("expires_in_hours must be between 1 and 8760.")
        death_clock = datetime.now(timezone.utc) + timedelta(hours=int(expires_in_hours))
        expires_at = death_clock.isoformat()

    # --- PATH A: CUSTOM ALIAS ---
    if custom_alias:
        if not is_valid_alias(custom_alias):
            raise ValueError("Alias must be 3-20 characters, letters, numbers, or hyphens.")

        # Check for collision before inserting
        existing_alias = url_model.find_by_code(custom_alias)
        if existing_alias:
            raise AliasTakenError("That custom alias is already taken.")

        return url_model.insert_url_with_alias(original_url, custom_alias, expires_at)

    # --- PATH B: STANDARD BASE62 ENCODING ---
    # FIX: Only deduplicate against active (non-expired) records
    existing_entry = url_model.find_by_original_url(original_url)
    if existing_entry:
        return existing_entry

    # FIX: No "PENDING" placeholder. Insert the row with short_code=NULL first,
    # then use the auto-increment ID to derive a guaranteed-unique Base62 code.
    new_id = url_model.insert_url(original_url, expires_at)
    short_code = encode(new_id)
    url_model.update_short_code(new_id, short_code)

    return url_model.find_by_id(new_id)  # type: ignore


def resolve_url(short_code: str) -> dict:
    """
    Look up a short code and increment its click counter.

    Returns:
        The URL record dict.

    Raises:
        KeyError: If the short code doesn't exist.
        ExpiredURLError: If the link has passed its expiration date.
    """
    record = url_model.find_by_code(short_code)
    if not record:
        raise KeyError(f"Short code '{short_code}' not found.")

    if record.get('expires_at'):
        expiration_date = datetime.fromisoformat(record['expires_at'])
        if expiration_date.tzinfo is None:
            expiration_date = expiration_date.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expiration_date:
            raise ExpiredURLError("This link has self-destructed.")

    url_model.increment_clicks(short_code)
    return record


def get_stats() -> list[dict]:
    """Return click analytics for all URLs. original_url is excluded by the model."""
    return url_model.get_all_urls()
