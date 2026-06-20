"""
test_board_service.py
Unit tests for board_service validation logic.
These tests exercise only the validation layer — no DB or Flask app context required.
"""
import pytest
from app.services.board_service import create_board, update_board


# ---------------------------------------------------------------------------
# create_board — title validation
# ---------------------------------------------------------------------------

class TestCreateBoardTitle:

    def test_missing_title_raises(self):
        with pytest.raises(ValueError, match="Board title is required"):
            create_board({"description": "No title here", "accent_color": "#ffffff"})

    def test_empty_string_title_raises(self):
        with pytest.raises(ValueError, match="Board title is required"):
            create_board({"title": "", "accent_color": "#ffffff"})

    def test_whitespace_only_title_raises(self):
        with pytest.raises(ValueError, match="Board title is required"):
            create_board({"title": "   ", "accent_color": "#ffffff"})


# ---------------------------------------------------------------------------
# create_board — accent_color validation
# ---------------------------------------------------------------------------

class TestCreateBoardAccentColor:

    def test_invalid_color_word_raises(self):
        with pytest.raises(ValueError, match="Invalid accent color"):
            create_board({"title": "Valid Title", "accent_color": "blue"})

    def test_invalid_color_no_hash_raises(self):
        with pytest.raises(ValueError, match="Invalid accent color"):
            create_board({"title": "Valid Title", "accent_color": "3b82f6"})

    def test_invalid_color_too_long_raises(self):
        with pytest.raises(ValueError, match="Invalid accent color"):
            create_board({"title": "Valid Title", "accent_color": "#1234567"})

    def test_invalid_color_too_short_raises(self):
        with pytest.raises(ValueError, match="Invalid accent color"):
            create_board({"title": "Valid Title", "accent_color": "#12"})

    def test_valid_6char_hex_passes(self):
        """A valid 6-char hex should not raise at the validation step."""
        # We expect this to fail at the DB step (no app context), not the validation step
        with pytest.raises(Exception) as exc_info:
            create_board({"title": "Valid Board", "accent_color": "#3b82f6"})
        # The exception must NOT be about the color
        assert "Invalid accent color" not in str(exc_info.value)

    def test_valid_3char_hex_passes(self):
        """A valid 3-char hex shorthand should not raise at the validation step."""
        with pytest.raises(Exception) as exc_info:
            create_board({"title": "Valid Board", "accent_color": "#fff"})
        assert "Invalid accent color" not in str(exc_info.value)

    def test_uppercase_hex_passes(self):
        """Hex colors are case-insensitive."""
        with pytest.raises(Exception) as exc_info:
            create_board({"title": "Valid Board", "accent_color": "#3B82F6"})
        assert "Invalid accent color" not in str(exc_info.value)


# ---------------------------------------------------------------------------
# update_board — validation
# ---------------------------------------------------------------------------

from unittest.mock import patch

class TestUpdateBoardValidation:

    @patch('app.services.board_service.board_model.get_board_by_id')
    def test_empty_title_raises(self, mock_get):
        """update_board raises if the new title is an empty string."""
        mock_get.return_value = {"id": 1, "title": "Old", "description": "", "accent_color": "#ffffff"}
        with pytest.raises(ValueError, match="Board title cannot be empty"):
            update_board(1, {"title": "   ", "accent_color": "#ffffff"})

    @patch('app.services.board_service.board_model.get_board_by_id')
    def test_invalid_color_raises_on_update(self, mock_get):
        mock_get.return_value = {"id": 1, "title": "Old", "description": "", "accent_color": "#ffffff"}
        with pytest.raises(ValueError, match="Invalid accent color"):
            update_board(1, {"title": "New Title", "accent_color": "not-a-color"})