from flask import Flask, request, jsonify   #type: ignore
from flask_cors import CORS                 #type: ignore
import bcrypt                               #type: ignore
import sqlite3                              #type: ignore

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'super-secret-project52-key'
DB_NAME = 'users.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    pass

if __name__ == '__main__':
    init_db()
    print("Auth Server Running!")
    app.run(debug=True, port=5000)