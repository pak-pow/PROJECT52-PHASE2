from app.models import card_model


def create_card(column_id, data):
    title = data.get('title', '').strip()
    if not title:
        raise ValueError("Card title is required")

    raw_desc = data.get('description', '')
    description = raw_desc.strip() if raw_desc else ''

    card_id = card_model.create_card(column_id, title, description)
    return card_model.get_card_by_id(card_id)


def update_card(card_id, data):
    existing = card_model.get_card_by_id(card_id)
    if not existing:
        raise ValueError("Card not found")

    title = data.get('title', existing['title']).strip()
    if not title:
        raise ValueError("Card title cannot be empty")

    # Guard against None description (field is optional in DB)
    raw_desc = data.get('description', existing['description'])
    description = raw_desc.strip() if raw_desc else ''

    card_model.update_card(card_id, title, description)
    return card_model.get_card_by_id(card_id)