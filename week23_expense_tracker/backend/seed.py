import sqlite3 
import os
from werkzeug.security import generate_password_hash #type: ignore

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'database.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql') 

def seed_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())

    cursor = conn.cursor()

    import secrets
    print("Securing admin credentials...")
    random_password = secrets.token_hex(6) # 12 character hex string
    secure_password = generate_password_hash(random_password)
    cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('admin', secure_password))
    admin_id = cursor.lastrowid
    print(f"Generated admin credentials: admin / {random_password}")

    mock_expenses = [
        (admin_id, 1200.00, 'Rent', 'May Rent', '2026-05-01'),
        (admin_id, 45.50, 'Food', 'Groceries', '2026-05-02'),
        (admin_id, 15.00, 'Food', 'Lunch', '2026-05-03'),
        (admin_id, 30.00, 'Transport', 'Gas', '2026-05-04'),
        (admin_id, 120.00, 'Entertainment', 'Concert Ticket', '2026-05-05'),
        (admin_id, 65.00, 'Food', 'Dinner Date', '2026-05-06')
    ]

    print("Injecting financial data...")
    cursor.executemany('''
        INSERT INTO expenses (user_id, amount, category, description, date) 
        VALUES (?, ?, ?, ?, ?)
    ''', mock_expenses)

    conn.commit()
    conn.close()
    print(f"Success! Admin created and {len(mock_expenses)} mock expenses added.")

if __name__ == '__main__':
    seed_database()