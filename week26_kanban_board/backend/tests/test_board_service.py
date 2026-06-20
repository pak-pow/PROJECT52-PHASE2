import pytest #type: ignore
from app.services.board_service import create_board

def test_create_board_missing_title():
    with pytest.raises(ValueError, match="Board title is required"):
        create_board({"description": "No title here", "accent_color": "#ffffff"})

def test_create_board_invalid_color_word():
    with pytest.raises(ValueError, match="Invalid accent color"):
        create_board({"title": "Valid Title", "accent_color": "blue"})

def test_create_board_invalid_color_hex():
    with pytest.raises(ValueError, match="Invalid accent color"):
        create_board({"title": "Valid Title", "accent_color": "#1234567"}) 