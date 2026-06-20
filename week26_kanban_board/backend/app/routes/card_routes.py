from flask import Blueprint, request, jsonify  # type: ignore
from app.services import card_service
from app.models import card_model

card_bp = Blueprint('cards', __name__)


# ---------------------------------------------------------------------------
# GET /api/columns/<column_id>/cards  — list all cards in a column
# ---------------------------------------------------------------------------
@card_bp.route('/api/columns/<int:column_id>/cards', methods=['GET'])
def get_cards(column_id):
    cards = card_model.get_cards_by_column(column_id)
    return jsonify(cards), 200


# ---------------------------------------------------------------------------
# POST /api/columns/<column_id>/cards  — create a card
# ---------------------------------------------------------------------------
@card_bp.route('/api/columns/<int:column_id>/cards', methods=['POST'])
def create_card(column_id):
    try:
        data = request.get_json() or {}
        new_card = card_service.create_card(column_id, data)
        return jsonify(new_card), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# ---------------------------------------------------------------------------
# GET /api/cards/<card_id>  — get a single card
# ---------------------------------------------------------------------------
@card_bp.route('/api/cards/<int:card_id>', methods=['GET'])
def get_card(card_id):
    card = card_model.get_card_by_id(card_id)
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    return jsonify(card), 200


# ---------------------------------------------------------------------------
# PUT /api/cards/<card_id>  — update a card
# ---------------------------------------------------------------------------
@card_bp.route('/api/cards/<int:card_id>', methods=['PUT'])
def update_card(card_id):
    try:
        data = request.get_json() or {}
        updated = card_service.update_card(card_id, data)
        return jsonify(updated), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# ---------------------------------------------------------------------------
# DELETE /api/cards/<card_id>  — delete a card
# ---------------------------------------------------------------------------
@card_bp.route('/api/cards/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    existing = card_model.get_card_by_id(card_id)
    if not existing:
        return jsonify({'error': 'Card not found'}), 404

    card_model.delete_card(card_id)
    return '', 204


# ---------------------------------------------------------------------------
# PATCH /api/columns/<column_id>/cards/reorder  — bulk-update card positions
# ---------------------------------------------------------------------------
@card_bp.route('/api/columns/<int:column_id>/cards/reorder', methods=['PATCH'])
def reorder_cards(column_id):
    data = request.get_json() or {}
    updates = data.get('updates', [])

    if not isinstance(updates, list):
        return jsonify({'error': 'updates must be a list of [card_id, position] pairs'}), 400

    card_model.update_card_positions(updates)
    return jsonify({'message': 'Cards reordered successfully'}), 200


# ---------------------------------------------------------------------------
# PATCH /api/cards/<card_id>/move  — move card to a different column
# ---------------------------------------------------------------------------
@card_bp.route('/api/cards/<int:card_id>/move', methods=['PATCH'])
def move_card(card_id):
    existing = card_model.get_card_by_id(card_id)
    if not existing:
        return jsonify({'error': 'Card not found'}), 404

    data = request.get_json() or {}
    new_column_id = data.get('column_id')
    new_position  = data.get('position', 0)

    if new_column_id is None:
        return jsonify({'error': 'column_id is required'}), 400

    card_model.move_card(card_id, new_column_id, new_position)
    return jsonify(card_model.get_card_by_id(card_id)), 200