from flask import Blueprint, jsonify, request #type: ignore
from app.models.expense import Expense

expenses_bp = Blueprint('expenses', __name__)

CURRENT_USER_ID = 1 

@expenses_bp.route('/', methods=['GET'])
def get_expenses():
    """Returns all raw expenses for the current user."""
    raw_expenses = Expense.get_all_by_user(CURRENT_USER_ID)

    expenses_list = [dict(row) for row in raw_expenses]
    return jsonify(expenses_list), 200

@expenses_bp.route('/summary', methods=['GET'])
def get_expense_summary():
    """Returns the aggregated total amount per category for Chart.js."""
    summary_data = Expense.get_aggregated_by_category(CURRENT_USER_ID)
    
    summary_list = [dict(row) for row in summary_data]
    return jsonify(summary_list), 200

@expenses_bp.route('/', methods=['POST'])
def add_expense():
    """Logs a new expense into the database."""
    data = request.get_json()
    
    if not data or not data.get('amount') or not data.get('category') or not data.get('date'):
        return jsonify({"error": "Missing required fields: amount, category, date"}), 400
        
    new_id = Expense.create(
        user_id=CURRENT_USER_ID,
        amount=data['amount'],
        category=data['category'],
        description=data.get('description', ''),
        date=data['date']
    )
    
    return jsonify({"message": "Expense logged successfully!", "id": new_id}), 201