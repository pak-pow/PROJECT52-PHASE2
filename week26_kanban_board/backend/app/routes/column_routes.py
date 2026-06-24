from flask import Blueprint, request, jsonify, g  # type: ignore
from app.models import column_model, board_model
from app.middlewares.auth_middleware import login_required

column_bp = Blueprint('columns', __name__)


# ---------------------------------------------------------------------------
# GET /api/boards/<board_id>/columns  — list all columns for a board
# ---------------------------------------------------------------------------
@column_bp.route('/api/boards/<int:board_id>/columns', methods=['GET'])
@login_required
def get_columns(board_id):
    board = board_model.get_board_by_id(board_id)
    if not board or board['user_id'] != g.user['id']:
        return jsonify({'error': 'Board not found'}), 404
        
    columns = column_model.get_columns_by_board(board_id)
    return jsonify(columns), 200


# ---------------------------------------------------------------------------
# POST /api/boards/<board_id>/columns  — create a column
# ---------------------------------------------------------------------------
@column_bp.route('/api/boards/<int:board_id>/columns', methods=['POST'])
@login_required
def create_column(board_id):
    board = board_model.get_board_by_id(board_id)
    if not board or board['user_id'] != g.user['id']:
        return jsonify({'error': 'Board not found'}), 404

    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Column title is required'}), 400

    column = column_model.create_column(board_id, title)
    return jsonify(column), 201


# ---------------------------------------------------------------------------
# PUT /api/columns/<column_id>  — rename a column
# ---------------------------------------------------------------------------
@column_bp.route('/api/columns/<int:column_id>', methods=['PUT'])
@login_required
def update_column(column_id):
    existing = column_model.get_column_by_id(column_id)
    if not existing:
        return jsonify({'error': 'Column not found'}), 404

    board = board_model.get_board_by_id(existing['board_id'])
    if not board or board['user_id'] != g.user['id']:
        return jsonify({'error': 'Column not found'}), 404

    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Column title is required'}), 400

    updated = column_model.update_column(column_id, title)
    return jsonify(updated), 200


# ---------------------------------------------------------------------------
# DELETE /api/columns/<column_id>  — delete a column (cascades cards)
# ---------------------------------------------------------------------------
@column_bp.route('/api/columns/<int:column_id>', methods=['DELETE'])
@login_required
def delete_column(column_id):
    existing = column_model.get_column_by_id(column_id)
    if not existing:
        return jsonify({'error': 'Column not found'}), 404

    board = board_model.get_board_by_id(existing['board_id'])
    if not board or board['user_id'] != g.user['id']:
        return jsonify({'error': 'Column not found'}), 404

    column_model.delete_column(column_id)
    return '', 204


# ---------------------------------------------------------------------------
# PATCH /api/boards/<board_id>/columns/reorder  — bulk-update column positions
# ---------------------------------------------------------------------------
@column_bp.route('/api/boards/<int:board_id>/columns/reorder', methods=['PATCH'])
@login_required
def reorder_columns(board_id):
    board = board_model.get_board_by_id(board_id)
    if not board or board['user_id'] != g.user['id']:
        return jsonify({'error': 'Board not found'}), 404

    data = request.get_json() or {}
    updates = data.get('updates', [])

    if not isinstance(updates, list):
        return jsonify({'error': 'updates must be a list of [column_id, position] pairs'}), 400

    # Verify that all columns belong to this board
    for item in updates:
        if not isinstance(item, list) or len(item) != 2:
            return jsonify({'error': 'invalid updates list format'}), 400
        col_id = item[0]
        col = column_model.get_column_by_id(col_id)
        if not col or col['board_id'] != board_id:
            return jsonify({'error': 'unauthorized column reordering'}), 400

    column_model.update_column_positions(updates)
    return jsonify({'message': 'Columns reordered successfully'}), 200