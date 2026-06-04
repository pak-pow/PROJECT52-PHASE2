from app.utils.db import get_db

class Expense:
    @staticmethod
    def get_all_by_user(user_id, limit=50, offset=0, start_date=None, end_date=None, category=None):
        """Fetches paginated expenses. Explicitly selects columns to prevent user_id data leak."""
        db = get_db()
        query = '''
            SELECT id, amount, category, description, date, created_at
            FROM expenses
            WHERE user_id = ?
        '''
        params = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if category and category != 'All':
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        return db.execute(query, tuple(params)).fetchall()

    @staticmethod
    def get_aggregated_by_category(user_id, start_date=None, end_date=None):
        """Groups expenses by category and sums totals. Supports optional date filtering."""
        db = get_db()
        query = "SELECT category, SUM(amount) as total_amount FROM expenses WHERE user_id = ?"
        params = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " GROUP BY category ORDER BY total_amount DESC"
        return db.execute(query, tuple(params)).fetchall()

    @staticmethod
    def create(user_id, amount, category, description, date):
        """Inserts a new raw expense row."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            '''INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)''',
            (user_id, amount, category, description, date)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def update(expense_id, user_id, amount, category, description, date):
        """Updates an existing expense. Returns rows affected for 404 detection."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            '''UPDATE expenses SET amount = ?, category = ?, description = ?, date = ?
               WHERE id = ? AND user_id = ?''',
            (amount, category, description, date, expense_id, user_id)
        )
        db.commit()
        return cursor.rowcount

    @staticmethod
    def delete(expense_id, user_id):
        """Deletes an expense. Returns rows affected for 404 detection."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', (expense_id, user_id))
        db.commit()
        return cursor.rowcount