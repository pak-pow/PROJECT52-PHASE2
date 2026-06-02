from app.utils.db import get_db

class Expense:
    @staticmethod
    def get_all_by_user(user_id, limit=50, offset=0):
        """Fetches paginated expenses. Explicitly selects columns to prevent user_id data leak."""
        db = get_db()
        query = '''
            SELECT id, amount, category, description, date, created_at
            FROM expenses
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT ? OFFSET ?
        '''
        return db.execute(query, (user_id, limit, offset)).fetchall()

    @staticmethod
    def get_aggregated_by_category(user_id, month=None, year=None):
        """Groups expenses by category and sums totals. Supports optional month/year filtering."""
        db = get_db()
        query = "SELECT category, SUM(amount) as total_amount FROM expenses WHERE user_id = ?"
        params = [user_id]

        if month:
            query += " AND strftime('%m', date) = ?"
            params.append(f"{int(month):02d}")  # Ensures format is '05', not '5'
        if year:
            query += " AND strftime('%Y', date) = ?"
            params.append(str(year))

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