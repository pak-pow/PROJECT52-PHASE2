"""
test_card_service.py
Unit tests for card_service validation logic.
These tests exercise only the validation layer — no DB or Flask app context required.
"""
import pytest
from app.services.card_service import create_card, update_card


# ---------------------------------------------------------------------------
# create_card — title validation
# ---------------------------------------------------------------------------

class TestCreateCardTitle:

    def test_missing_title_raises(self):
        with pytest.raises(ValueError, match="Card title is required"):
            create_card(1, {"description": "No title provided"})

    def test_empty_string_title_raises(self):
        with pytest.raises(ValueError, match="Card title is required"):
            create_card(1, {"title": "", "description": "Some description"})

    def test_whitespace_only_title_raises(self):
        with pytest.raises(ValueError, match="Card title is required"):
            create_card(1, {"title": "   ", "description": "Some description"})

    def test_valid_title_passes_validation(self):
        """A valid title should not raise a ValueError — it will only fail at DB level."""
        with pytest.raises(Exception) as exc_info:
            create_card(1, {"title": "Fix the bug", "description": "Details here"})
        assert "Card title is required" not in str(exc_info.value)

    def test_valid_title_no_description_passes_validation(self):
        """Description is optional — omitting it should not raise ValueError."""
        with pytest.raises(Exception) as exc_info:
            create_card(1, {"title": "A card without description"})
        assert "Card title is required" not in str(exc_info.value)


# ---------------------------------------------------------------------------
# update_card — validation
# ---------------------------------------------------------------------------

from unittest.mock import patch

class TestUpdateCardValidation:

    @patch('app.services.card_service.card_model.get_card_by_id')
    def test_card_not_found_raises(self, mock_get):
        """update_card raises ValueError when the card ID doesn't exist."""
        mock_get.return_value = None
        with pytest.raises(ValueError, match="Card not found"):
            update_card(99999, {"title": "Updated title"})

    @patch('app.services.card_service.card_model.get_card_by_id')
    def test_empty_title_on_update_raises(self, mock_get):
        mock_get.return_value = {"id": 1, "title": "Old", "description": ""}
        with pytest.raises(ValueError, match="Card title cannot be empty"):
            update_card(1, {"title": ""})

    @patch('app.services.card_service.card_model.get_card_by_id')
    def test_none_description_does_not_crash(self, mock_get):
        """
        Regression test: update_card used to crash with AttributeError when the
        existing description was None. Verify the fix.
        """
        mock_get.return_value = {"id": 1, "title": "Old", "description": None}
        # Should not crash with AttributeError
        # We also mock update_card inside card_model so it doesn't hit DB
        with patch('app.services.card_service.card_model.update_card'):
            update_card(1, {"title": "Title", "description": None})