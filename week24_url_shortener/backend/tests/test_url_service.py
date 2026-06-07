import pytest #type:ignore
from app.services import url_service
from app.models import url_model

def test_invalid_url_rejected(app):
    """Ensure strings without http:// or https:// are rejected."""
    with app.app_context():
        with pytest.raises(ValueError, match="Invalid URL"):
            url_service.shorten_url("google.com") 
            
        with pytest.raises(ValueError, match="Invalid URL"):
            url_service.shorten_url("not-a-url")

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
        assert updated_record['clicks'] == 2 # type: ignore