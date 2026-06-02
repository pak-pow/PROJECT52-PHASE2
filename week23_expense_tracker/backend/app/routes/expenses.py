from flask import Blueprint, jsonify, request #type: ignore
from app.models.expense import Expense
from flask_jwt_extended import jwt_required, get_jwt_identity #type: ignore

expenses_bp = Blueprint('expenses', __name__)

def validate_expense_data(data):
    """Helper to validate expense payloads. Returns an error string or None."""
    if not data:
        return "No data provided"
    
    if data.get('amount') is None: 
        return "Missing amount"
    
    if not isinstance(data.get('amount'), (int, float)):
        return "Amount must be a number"
    
    if not data.get('category'):
        return "Missing category"
    
    if not data.get('date'):
        return "Missing date"
    return None

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

    # Support optional filtering: /summary?month=05&year=2026
    month = request.args.get('month')
    year = request.args.get('year')

    summary_data = Expense.get_aggregated_by_category(current_user_id, month, year)
    return jsonify([dict(row) for row in summary_data]), 200

@expenses_bp.route('/', methods=['POST'])
@jwt_required()
def add_expense():
    data = request.get_json()
    error = validate_expense_data(data)
    if error:
        return jsonify({"error": error}), 400

    new_id = Expense.create(
        user_id=get_jwt_identity(),
        amount=data['amount'],
        category=data['category'],
        description=data.get('description', ''),
        date=data['date']
    )
    return jsonify({"message": "Expense logged successfully!", "id": new_id}), 201

@expenses_bp.route('/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    data = request.get_json()
    error = validate_expense_data(data)
    if error:
        return jsonify({"error": error}), 400

    rows_affected = Expense.update(
        expense_id=expense_id,
        user_id=get_jwt_identity(),
        amount=data['amount'],
        category=data['category'],
        description=data.get('description', ''),
        date=data['date']
    )

    if rows_affected == 0:
        return jsonify({"error": "Expense not found or unauthorized"}), 404
    return jsonify({"message": "Expense updated successfully!"}), 200

@expenses_bp.route('/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    rows_affected = Expense.delete(expense_id, get_jwt_identity())

    if rows_affected == 0:
        return jsonify({"error": "Expense not found or unauthorized"}), 404

    return jsonify({"message": f"Expense {expense_id} deleted successfully!"}), 200