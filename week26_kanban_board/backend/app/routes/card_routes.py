from flask import Blueprint, request, jsonify #type: ignore
from app.services import card_service
from app.models import card_model

card_bp = Blueprint('cards', __name__)

@card_bp.route('/api/columns/<int:column_id>/cards', methods=['POST'])
def create_card(column_id):
    try:
        data = request.get_json() or {}
        new_card = card_service.create_card(column_id, data)
        return jsonify(new_card), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@card_bp.route('/api/cards/<int:card_id>', methods=['PUT'])
def update_card(card_id):
    try:
        data = request.get_json() or {}
        updated = card_service.update_card(card_id, data)
        return jsonify(updated), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@card_bp.route('/api/cards/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    card_model.delete_card(card_id)
    return '', 204

@card_bp.route('/api/columns/<int:column_id>/cards/reorder', methods=['PATCH'])
def reorder_cards(column_id):
    data = request.get_json() or {}
    updates = data.get('updates', [])
    card_model.update_card_positions(updates)
    return jsonify({'message': 'Cards reordered successfully'}), 200

@card_bp.route('/api/cards/<int:card_id>/move', methods=['PATCH'])
def move_card(card_id):
    data = request.get_json() or {}
    new_column_id = data.get('column_id')
    new_position = data.get('position', 0)
    
    if new_column_id is None:
        return jsonify({'error': 'column_id is required'}), 400
        
    card_model.move_card(card_id, new_column_id, new_position)
    return jsonify({'message': 'Card moved successfully'}), 200