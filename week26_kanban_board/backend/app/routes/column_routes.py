from flask import Blueprint, request, jsonify  # type: ignore
from app.models import column_model

column_bp = Blueprint('columns', __name__)


# ---------------------------------------------------------------------------
# GET /api/boards/<board_id>/columns  — list all columns for a board
# ---------------------------------------------------------------------------
@column_bp.route('/api/boards/<int:board_id>/columns', methods=['GET'])
def get_columns(board_id):
    columns = column_model.get_columns_by_board(board_id)
    return jsonify(columns), 200


# ---------------------------------------------------------------------------
# POST /api/boards/<board_id>/columns  — create a column
# ---------------------------------------------------------------------------
@column_bp.route('/api/boards/<int:board_id>/columns', methods=['POST'])
def create_column(board_id):
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
def update_column(column_id):
    existing = column_model.get_column_by_id(column_id)
    if not existing:
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
def delete_column(column_id):
    existing = column_model.get_column_by_id(column_id)
    if not existing:
        return jsonify({'error': 'Column not found'}), 404

    column_model.delete_column(column_id)
    return '', 204


# ---------------------------------------------------------------------------
# PATCH /api/boards/<board_id>/columns/reorder  — bulk-update column positions
# ---------------------------------------------------------------------------
@column_bp.route('/api/boards/<int:board_id>/columns/reorder', methods=['PATCH'])
def reorder_columns(board_id):
    data = request.get_json() or {}
    updates = data.get('updates', [])

    if not isinstance(updates, list):
        return jsonify({'error': 'updates must be a list of [column_id, position] pairs'}), 400

    column_model.update_column_positions(updates)
    return jsonify({'message': 'Columns reordered successfully'}), 200