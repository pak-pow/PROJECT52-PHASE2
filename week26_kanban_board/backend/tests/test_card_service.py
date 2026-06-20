import pytest #type: ignore
from app.services.card_service import create_card

def test_create_card_missing_title():
    # Expect the service to reject a card without a title
    with pytest.raises(ValueError, match="Card title is required"):
        create_card(1, {"description": "This is a task description but I forgot the headline"})