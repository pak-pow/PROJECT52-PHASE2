import sqlite3
import os
from werkzeug.security import generate_password_hash #type: ignore

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'database.db')

def seed_database():
    if not os.path.exists(DB_PATH):
        print("Error: Database not found. Run 'python run.py' first to build it.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Securing admin credentials...")
    secure_password = generate_password_hash('admin123')

    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    admin_user = cursor.fetchone()

    if not admin_user:
        cursor.execute('''
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        ''', ('admin', secure_password))
        author_id = cursor.lastrowid
    else:
        author_id = admin_user[0]
        cursor.execute('''
            UPDATE users SET password_hash = ? WHERE id = ?
        ''', (secure_password, author_id))

    mock_posts = [
        ("My First CMS Post", "This is the content of the first post.", author_id, 'published'),
        ("Why Python is Awesome", "Flask is great.", author_id, 'published'),
        ("Secret Upcoming Feature", "This is a draft! The public shouldn't see this yet.", author_id, 'draft')
    ]

    print("Injecting mock data...")
    cursor.executemany('INSERT INTO posts (title, content, author_id, status) VALUES (?, ?, ?, ?)', mock_posts)
    
    conn.commit()
    conn.close()
    print(f"Success! Admin secured and {len(mock_posts)} dummy posts added.")

if __name__ == '__main__':
    seed_database()