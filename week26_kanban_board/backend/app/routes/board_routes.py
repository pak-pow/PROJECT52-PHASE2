from flask import Blueprint, request, jsonify #type: ignore
from app.services import board_service

board_bp = Blueprint('boards', __name__, url_prefix='/api/boards')

@board_bp.route('', methods=['GET'])
def get_boards():
    return jsonify(board_service.get_all_boards()), 200

@board_bp.route('/<int:board_id>', methods=['GET'])
def get_board(board_id):
    try:
        board = board_service.get_board_with_details(board_id)
        return jsonify(board), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@board_bp.route('', methods=['POST'])
def create_board():
    try:
        data = request.get_json() or {}
        new_board = board_service.create_board(data)
        return jsonify(new_board), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@board_bp.route('/<int:board_id>', methods=['PUT'])
def update_board(board_id):
    try:
        data = request.get_json() or {}
        updated = board_service.update_board(board_id, data)
        return jsonify(updated), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@board_bp.route('/<int:board_id>', methods=['DELETE'])
def delete_board(board_id):
    try:
        board_service.delete_board(board_id)
        return '', 204
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@board_bp.route('/reorder', methods=['PATCH'])
def reorder_boards():
    try:
        data = request.get_json() or {}
        updates = data.get('updates')
        board_service.reorder_boards(updates)
        return jsonify({'message': 'Boards reordered successfully'}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400