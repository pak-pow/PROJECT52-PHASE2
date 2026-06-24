from flask import Blueprint, request, jsonify, g #type: ignore
from app.services import board_service
from app.middlewares.auth_middleware import login_required

board_bp = Blueprint('boards', __name__, url_prefix='/api/boards')

@board_bp.route('', methods=['GET'])
@login_required
def get_boards():
    return jsonify(board_service.get_all_boards(g.user['id'])), 200

@board_bp.route('/<int:board_id>', methods=['GET'])
@login_required
def get_board(board_id):
    try:
        board = board_service.get_board_with_details(g.user['id'], board_id)
        return jsonify(board), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@board_bp.route('', methods=['POST'])
@login_required
def create_board():
    try:
        data = request.get_json() or {}
        new_board = board_service.create_board(g.user['id'], data)
        return jsonify(new_board), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@board_bp.route('/<int:board_id>', methods=['PUT'])
@login_required
def update_board(board_id):
    try:
        data = request.get_json() or {}
        updated = board_service.update_board(g.user['id'], board_id, data)
        return jsonify(updated), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@board_bp.route('/<int:board_id>', methods=['DELETE'])
@login_required
def delete_board(board_id):
    try:
        board_service.delete_board(g.user['id'], board_id)
        return '', 204
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@board_bp.route('/reorder', methods=['PATCH'])
@login_required
def reorder_boards():
    try:
        data = request.get_json() or {}
        updates = data.get('updates')
        board_service.reorder_boards(g.user['id'], updates)
        return jsonify({'message': 'Boards reordered successfully'}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400