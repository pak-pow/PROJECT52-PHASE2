from flask import Blueprint, jsonify, request #type: ignore
from app.models.expense import Expense
from flask_jwt_extended import jwt_required, get_jwt_identity #type: ignore
from datetime import datetime

expenses_bp = Blueprint('expenses', __name__)

def validate_expense_data(data):
    """Strictly validates and sanitizes an incoming expense payload.
    Returns (sanitized_data, None) on success or (None, error_message) on failure.
    """
    if not data:
        return None, "No data provided"

    # 1. Amount validation
    amount = data.get('amount')
    if amount is None or not isinstance(amount, (int, float)):
        return None, "Amount must be a valid number"
    if amount <= 0 or amount > 999999:
        return None, "Amount must be between 0.01 and 999,999"
    amount = round(float(amount), 2)  # Prevent float precision bugs

    # 2. String sanitization
    category = data.get('category', '').strip()
    if not category:
        return None, "Missing category"
    if len(category) > 50:
        return None, "Category too long (max 50 characters)"

    description = data.get('description', '').strip()
    if len(description) > 255:
        return None, "Description too long (max 255 characters)"

    # 3. Date validation — force strict YYYY-MM-DD format
    date_str = data.get('date')
    if not date_str:
        return None, "Missing date"
    try:
        valid_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        return None, "Invalid date format. Use YYYY-MM-DD"

    sanitized = {
        "amount": amount,
        "category": category,
        "description": description,
        "date": valid_date
    }
    return sanitized, None


def parse_date_param(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        return None

@expenses_bp.route('/', methods=['GET'])
@jwt_required()
def get_expenses():
    current_user_id = get_jwt_identity()

    # Pagination: ?page=1&limit=50
    page = max(request.args.get('page', 1, type=int), 1)
    limit = min(request.args.get('limit', 50, type=int), 200)
    offset = (page - 1) * limit

    # Filtering
    start_date = parse_date_param(request.args.get('start_date'))
    end_date = parse_date_param(request.args.get('end_date'))
    
    category = request.args.get('category')
    if category and len(category) > 50:
        category = category[:50] # Or handle as error, truncating is safer to prevent long query string attacks

    raw_expenses = Expense.get_all_by_user(
        current_user_id, 
        limit=limit, 
        offset=offset,
        start_date=start_date,
        end_date=end_date,
        category=category
    )
    return jsonify([dict(row) for row in raw_expenses]), 200


@expenses_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_expense_summary():
    current_user_id = get_jwt_identity()

    # Optional date filtering
    start_date = parse_date_param(request.args.get('start_date'))
    end_date = parse_date_param(request.args.get('end_date'))

    summary_data = Expense.get_aggregated_by_category(
        current_user_id,
        start_date=start_date,
        end_date=end_date
    )
    return jsonify([dict(row) for row in summary_data]), 200


@expenses_bp.route('/', methods=['POST'])
@jwt_required()
def add_expense():
    clean_data, error = validate_expense_data(request.get_json())
    if error:
        return jsonify({"error": error}), 400

    new_id = Expense.create(
        user_id=get_jwt_identity(),
        amount=clean_data['amount'],
        category=clean_data['category'],
        description=clean_data['description'],
        date=clean_data['date']
    )
    return jsonify({"message": "Expense logged successfully!", "id": new_id}), 201


@expenses_bp.route('/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    clean_data, error = validate_expense_data(request.get_json())
    if error:
        return jsonify({"error": error}), 400

    rows_affected = Expense.update(
        expense_id=expense_id,
        user_id=get_jwt_identity(),
        amount=clean_data['amount'],
        category=clean_data['category'],
        description=clean_data['description'],
        date=clean_data['date']
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