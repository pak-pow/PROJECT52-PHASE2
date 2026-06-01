from flask import Blueprint, jsonify, request #type: ignore
from app.models.expense import Expense
from flask_jwt_extended import jwt_required, get_jwt_identity #type: ignore

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/', methods=['GET'])
@jwt_required() 
def get_expenses():
    current_user_id = get_jwt_identity() 
    raw_expenses = Expense.get_all_by_user(current_user_id)
    return jsonify([dict(row) for row in raw_expenses]), 200

@expenses_bp.route('/summary', methods=['GET'])
@jwt_required() 
def get_expense_summary():
    current_user_id = get_jwt_identity()
    summary_data = Expense.get_aggregated_by_category(current_user_id)
    return jsonify([dict(row) for row in summary_data]), 200

@expenses_bp.route('/', methods=['POST'])
@jwt_required() 
def add_expense():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    if not data or not data.get('amount') or not data.get('category') or not data.get('date'):
        return jsonify({"error": "Missing required fields"}), 400
        
    new_id = Expense.create(
        user_id=current_user_id,
        amount=data['amount'],
        category=data['category'],
        description=data.get('description', ''),
        date=data['date']
    )
    return jsonify({"message": "Expense logged successfully!", "id": new_id}), 201

@expenses_bp.route('/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    current_user_id = get_jwt_identity()
    Expense.delete(expense_id, current_user_id)
    
    return jsonify({"message": f"Expense {expense_id} deleted successfully!"}), 200