import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DB_PATH = os.path.join(DATA_DIR, 'database.db')

def initialize_db():
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            category    TEXT NOT NULL,
            price       REAL NOT NULL,
            image       TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_amount REAL NOT NULL,
            total_items INTEGER NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('DELETE FROM products')
    
    products = [
        ("Sony WH-1000XM5", "Electronics", 348.00, "🎧"),
        ("Mechanical Keyboard", "Electronics", 120.50, "⌨️"),
        ("Ergonomic Office Chair", "Furniture", 299.99, "🪑"),
        ("Ceramic Coffee Mug", "Home", 18.00, "☕"),
        ("Python Crash Course", "Books", 25.99, "📘"),
        ("Gaming Mouse", "Electronics", 60.00, "🖱️")
    ]

    cursor.executemany('''
        INSERT INTO products (name, category, price, image)
        VALUES (?, ?, ?, ?)
    ''', products)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized successfully at: {DB_PATH}")
    
if __name__ == '__main__':
    initialize_db()