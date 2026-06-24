from flask import Blueprint, request, jsonify, g  # type: ignore
from app.services import card_service
from app.models import card_model, column_model, board_model
from app.middlewares.auth_middleware import login_required

card_bp = Blueprint('cards', __name__)

def verify_column_ownership(column_id, user_id):
    col = column_model.get_column_by_id(column_id)
    if not col:
        return False
    board = board_model.get_board_by_id(col['board_id'])
    return board and board['user_id'] == user_id

def verify_card_ownership(card_id, user_id):
    card = card_model.get_card_by_id(card_id)
    if not card:
        return False
    return verify_column_ownership(card['column_id'], user_id)


# ---------------------------------------------------------------------------
# GET /api/columns/<column_id>/cards  — list all cards in a column
# ---------------------------------------------------------------------------
@card_bp.route('/api/columns/<int:column_id>/cards', methods=['GET'])
@login_required
def get_cards(column_id):
    if not verify_column_ownership(column_id, g.user['id']):
        return jsonify({'error': 'Column not found'}), 404
    cards = card_model.get_cards_by_column(column_id)
    return jsonify(cards), 200


# ---------------------------------------------------------------------------
# POST /api/columns/<column_id>/cards  — create a card
# ---------------------------------------------------------------------------
@card_bp.route('/api/columns/<int:column_id>/cards', methods=['POST'])
@login_required
def create_card(column_id):
    if not verify_column_ownership(column_id, g.user['id']):
        return jsonify({'error': 'Column not found'}), 404
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
@login_required
def get_card(card_id):
    if not verify_card_ownership(card_id, g.user['id']):
        return jsonify({'error': 'Card not found'}), 404
    card = card_model.get_card_by_id(card_id)
    return jsonify(card), 200


# ---------------------------------------------------------------------------
# PUT /api/cards/<card_id>  — update a card
# ---------------------------------------------------------------------------
@card_bp.route('/api/cards/<int:card_id>', methods=['PUT'])
@login_required
def update_card(card_id):
    if not verify_card_ownership(card_id, g.user['id']):
        return jsonify({'error': 'Card not found'}), 404
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
@login_required
def delete_card(card_id):
    if not verify_card_ownership(card_id, g.user['id']):
        return jsonify({'error': 'Card not found'}), 404
    card_model.delete_card(card_id)
    return '', 204


# ---------------------------------------------------------------------------
# PATCH /api/columns/<column_id>/cards/reorder  — bulk-update card positions
# ---------------------------------------------------------------------------
@card_bp.route('/api/columns/<int:column_id>/cards/reorder', methods=['PATCH'])
@login_required
def reorder_cards(column_id):
    if not verify_column_ownership(column_id, g.user['id']):
        return jsonify({'error': 'Column not found'}), 404
    data = request.get_json() or {}
    updates = data.get('updates', [])

    if not isinstance(updates, list):
        return jsonify({'error': 'updates must be a list of [card_id, position] pairs'}), 400

    for item in updates:
        if not isinstance(item, list) or len(item) != 2:
            return jsonify({'error': 'invalid updates list format'}), 400
        card_id = item[0]
        if not verify_card_ownership(card_id, g.user['id']):
            return jsonify({'error': 'unauthorized card reordering'}), 400

    card_model.update_card_positions(updates)
    return jsonify({'message': 'Cards reordered successfully'}), 200


# ---------------------------------------------------------------------------
# PATCH /api/cards/<card_id>/move  — move card to a different column
# ---------------------------------------------------------------------------
@card_bp.route('/api/cards/<int:card_id>/move', methods=['PATCH'])
@login_required
def move_card(card_id):
    if not verify_card_ownership(card_id, g.user['id']):
        return jsonify({'error': 'Card not found'}), 404

    data = request.get_json() or {}
    new_column_id = data.get('column_id')
    new_position  = data.get('position', 0)

    if new_column_id is None:
        return jsonify({'error': 'column_id is required'}), 400

    if not verify_column_ownership(new_column_id, g.user['id']):
        return jsonify({'error': 'unauthorized destination column'}), 400

    card_model.move_card(card_id, new_column_id, new_position)
    return jsonify(card_model.get_card_by_id(card_id)), 200