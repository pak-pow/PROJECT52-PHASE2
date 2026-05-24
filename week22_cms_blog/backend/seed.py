import sqlite3
import os

# Find the database path safely
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'database.db')

def seed_database():
    if not os.path.exists(DB_PATH):
        print("Error: Database not found. Run 'python run.py' first to build it.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Get the ID of our default Admin user
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    admin_user = cursor.fetchone()
    
    if not admin_user:
        print("Error: Admin user not found.")
        return
        
    author_id = admin_user[0]

    mock_posts = [
        ("My First CMS Post", "This is the content of the first post. The API is working perfectly!", author_id),
        ("Why Python is Awesome", "Flask and the Application Factory pattern make building scalable backends so satisfying.", author_id),
        ("Week 22 Progress", "Building a custom CMS teaches you exactly how WordPress actually works under the hood.", author_id),
        ("The Power of SQLite", "It might be a simple file, but SQLite is incredibly fast for local development.", author_id),
        ("Hello World!", "Just another mock data post to fill up the database so our frontend looks good.", author_id)
    ]

    # 3. Inject the data
    print("Injecting mock data...")
    cursor.executemany('INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)', mock_posts)
    
    conn.commit()
    conn.close()
    print(f"Success! {len(mock_posts)} dummy posts added to the database.")

if __name__ == '__main__':
    seed_database()