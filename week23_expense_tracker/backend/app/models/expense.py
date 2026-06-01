from app.utils.db import get_db

class Expense:
    @staticmethod
    def get_all_by_user(user_id):
        """Fetches the raw, un-aggregated list of expenses for the table view."""
        db = get_db()
        return db.execute('SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC', (user_id,)).fetchall()

    @staticmethod
    def get_aggregated_by_category(user_id):
        """Groups expenses by category and adds up the total amount for Chart.js."""
        
        db = get_db()
        
        query = '''
            SELECT category, SUM(amount) as total_amount
            FROM expenses
            WHERE user_id = ?
            GROUP BY category
            ORDER BY total_amount DESC
        '''
        return db.execute(query, (user_id,)).fetchall()

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
    def delete(expense_id, user_id):
        """Deletes an expense, ensuring it belongs to the requesting user."""
        db = get_db()
        db.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', (expense_id, user_id))
        db.commit()