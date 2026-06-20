from flask import Blueprint, request, jsonify #type: ignore
from app.models import column_model

column_bp = Blueprint('columns', __name__)

@column_bp.route('/api/boards/<int:board_id>/columns', methods=['POST'])
def create_column(board_id):
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Column title is required'}), 400
    
    col_id = column_model.create_column(board_id, title)
    return jsonify({'id': col_id, 'board_id': board_id, 'title': title}), 201

@column_bp.route('/api/columns/<int:column_id>', methods=['PUT'])
def update_column(column_id):
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Column title is required'}), 400
    
    column_model.update_column(column_id, title)
    return jsonify({'message': 'Column updated'}), 200

@column_bp.route('/api/columns/<int:column_id>', methods=['DELETE'])
def delete_column(column_id):
    column_model.delete_column(column_id)
    return '', 204

@column_bp.route('/api/boards/<int:board_id>/columns/reorder', methods=['PATCH'])
def reorder_columns(board_id):
    data = request.get_json() or {}
    updates = data.get('updates', []) 
    column_model.update_column_positions(updates)
    return jsonify({'message': 'Columns reordered successfully'}), 200