import re
from app.models import board_model, column_model, card_model

def get_all_boards():
    return board_model.get_all_boards()

def get_board_with_details(board_id):
    board = board_model.get_board_by_id(board_id)
    if not board:
        raise ValueError("Board not found")
    
    columns = column_model.get_columns_by_board(board_id)
    
    for col in columns:
        col['cards'] = card_model.get_cards_by_column(col['id'])
    
    board['columns'] = columns
    return board

def create_board(data):
    title = data.get('title', '').strip()
    if not title:
        raise ValueError("Board title is required")
        
    accent_color = data.get('accent_color', '#3b82f6').strip()
    if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', accent_color):
        raise ValueError("Invalid accent color. Must be a valid hex code (e.g., #3b82f6)")
        
    description = data.get('description', '').strip()
    
    board_id = board_model.create_board(title, description, accent_color)
    return board_model.get_board_by_id(board_id)

def update_board(board_id, data):
    existing = board_model.get_board_by_id(board_id)
    if not existing:
        raise ValueError("Board not found")
        
    title = data.get('title', existing['title']).strip()
    if not title:
        raise ValueError("Board title cannot be empty")
        
    accent_color = data.get('accent_color', existing['accent_color']).strip()
    if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', accent_color):
        raise ValueError("Invalid accent color")
        
    description = data.get('description', existing['description']).strip()
    
    board_model.update_board(board_id, title, description, accent_color)
    return board_model.get_board_by_id(board_id)

def delete_board(board_id):
    existing = board_model.get_board_by_id(board_id)
    if not existing:
        raise ValueError("Board not found")
    board_model.delete_board(board_id)

def reorder_boards(updates):
    if not isinstance(updates, list):
        raise ValueError("Updates must be a list")
    for item in updates:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError("Each update must be a [board_id, position] list")
    board_model.reorder_boards(updates)