from app.models import card_model

def create_card(column_id, data):
    title = data.get('title', '').strip()
    if not title:
        raise ValueError("Card title is required")
        
    description = data.get('description', '').strip()
    
    card_id = card_model.create_card(column_id, title, description)
    return card_model.get_card_by_id(card_id)

def update_card(card_id, data):
    existing = card_model.get_card_by_id(card_id)
    if not existing:
        raise ValueError("Card not found")
        
    title = data.get('title', existing['title']).strip()
    if not title:
        raise ValueError("Card title cannot be empty")
        
    description = data.get('description', existing['description']).strip()
    
    card_model.update_card(card_id, title, description)
    return card_model.get_card_by_id(card_id)