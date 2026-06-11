import pytest  # type:ignore
from app.services import url_service
from app.models import url_model
from app.services.url_service import AliasTakenError


# ---------------------------------------------------------------------------
# URL Validation
# ---------------------------------------------------------------------------

def test_invalid_url_rejected(app):
    """Ensure strings without http:// or https:// are rejected."""
    with app.app_context():
        with pytest.raises(ValueError, match="Invalid URL"):
            url_service.shorten_url("google.com")
        with pytest.raises(ValueError, match="Invalid URL"):
            url_service.shorten_url("not-a-url")


def test_empty_url_rejected(app):
    """Ensure an empty string or whitespace-only URL is rejected."""
    with app.app_context():
        with pytest.raises(ValueError, match="URL cannot be empty"):
            url_service.shorten_url("")
        with pytest.raises(ValueError, match="URL cannot be empty"):
            url_service.shorten_url("   ")


# ---------------------------------------------------------------------------
# Input Type Validation (prevents 500 TypeError crashes)
# ---------------------------------------------------------------------------

def test_non_string_custom_alias_rejected(app):
    """Passing a non-string custom_alias must raise ValueError, not a 500 TypeError."""
    with app.app_context():
        with pytest.raises(ValueError, match="custom_alias must be a string"):
            url_service.shorten_url("https://www.example.com", custom_alias=123)


def test_non_numeric_expires_in_hours_rejected(app):
    """Passing a non-numeric expires_in_hours must raise ValueError, not a 500 TypeError."""
    with app.app_context():
        with pytest.raises(ValueError, match="expires_in_hours must be a number"):
            url_service.shorten_url("https://www.example.com", expires_in_hours="tomorrow")


def test_negative_expires_in_hours_rejected(app):
    """Negative expiry values must be rejected."""
    with app.app_context():
        with pytest.raises(ValueError, match="expires_in_hours must be between"):
            url_service.shorten_url("https://www.example.com", expires_in_hours=-5)


# ---------------------------------------------------------------------------
# Base62 Standard Flow
# ---------------------------------------------------------------------------

def test_shorten_valid_url(app):
    """Ensure a valid URL generates a short code and saves to the DB."""
    with app.app_context():
        record = url_service.shorten_url("https://www.github.com")
        assert record['original_url'] == "https://www.github.com"
        assert record['short_code'] is not None
        assert record['clicks'] == 0


def test_deduplication_returns_existing_code(app):
    """If the same URL is submitted twice, it should return the SAME short code."""
    with app.app_context():
        record1 = url_service.shorten_url("https://www.python.org")
        record2 = url_service.shorten_url("https://www.python.org")
        assert record1['id'] == record2['id']
        assert record1['short_code'] == record2['short_code']


def test_resolve_url_increments_clicks(app):
    """Resolving a short code should return the URL and increment the click counter."""
    with app.app_context():
        record = url_service.shorten_url("https://www.example.com")
        short_code = record['short_code']
        url_service.resolve_url(short_code)
        url_service.resolve_url(short_code)
        updated_record = url_model.find_by_code(short_code)
        assert updated_record['clicks'] == 2  # type: ignore


def test_no_pending_placeholder_in_db(app):
    """The PENDING placeholder bug must not exist — short_code is never literally 'PENDING'."""
    with app.app_context():
        record = url_service.shorten_url("https://www.wikipedia.org")
        assert record['short_code'] != "PENDING"
        # Also confirm no row in DB has short_code='PENDING'
        pending = url_model.find_by_code("PENDING")
        assert pending is None


# ---------------------------------------------------------------------------
# Custom Alias Flow
# ---------------------------------------------------------------------------

def test_custom_alias_success(app):
    """Pass a custom alias and ensure it creates the URL exactly as requested."""
    with app.app_context():
        record = url_service.shorten_url("https://www.google.com", custom_alias="summer-sale")
        assert record['short_code'] == "summer-sale"
        assert record['original_url'] == "https://www.google.com"


def test_custom_alias_collision(app):
    """Creating the same alias twice must raise AliasTakenError, not a generic KeyError."""
    with app.app_context():
        url_service.shorten_url("https://www.apple.com", custom_alias="my-sale")
        with pytest.raises(AliasTakenError, match="That custom alias is already taken."):
            url_service.shorten_url("https://www.microsoft.com", custom_alias="my-sale")


def test_custom_alias_invalid_format(app):
    """An alias with spaces or symbols must raise ValueError."""
    with app.app_context():
        with pytest.raises(ValueError, match="Alias must be 3-20 characters"):
            url_service.shorten_url("https://www.tesla.com", custom_alias="my alias@!")


def test_pending_alias_does_not_cause_dos(app):
    """
    Regression test for the PENDING DoS bug.
    A user registering 'PENDING' as a custom alias must NOT break standard link generation.
    """
    with app.app_context():
        # Register "PENDING" as a custom alias — this used to DoS standard shortening
        url_service.shorten_url("https://www.evil.com", custom_alias="PENDING")

        # Standard shortening for a different URL must still work without crashing
        record = url_service.shorten_url("https://www.innocent.com")
        assert record['short_code'] is not None
        assert record['short_code'] != "PENDING"