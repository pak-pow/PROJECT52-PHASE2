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
        ("My First CMS Post", "This is the content of the first post. The API is working perfectly!", author_id),
        ("Why Python is Awesome", "Flask and the Application Factory pattern make building scalable backends so satisfying.", author_id),
        ("Week 22 Progress", "Building a custom CMS teaches you exactly how WordPress actually works under the hood.", author_id),
        ("The Power of SQLite", "It might be a simple file, but SQLite is incredibly fast for local development.", author_id),
        ("Hello World!", "Just another mock data post to fill up the database so our frontend looks good.", author_id)
    ]

    print("Injecting mock data...")
    cursor.executemany('INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)', mock_posts)
    
    conn.commit()
    conn.close()
    print(f"Success! Admin secured and {len(mock_posts)} dummy posts added.")

if __name__ == '__main__':
    seed_database()