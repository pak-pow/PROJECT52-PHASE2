from flask import Flask, request, jsonify   #type: ignore
from flask_cors import CORS                 #type: ignore
import bcrypt                               #type: ignore
import sqlite3                              #type: ignore
import jwt                                  #type: ignore
import datetime

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
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': "Username and Password are required"}), 400

    # hashing the password using bcrypt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # save the user to the database
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash) VALUES(?, ?)", (username, hashed_password))
        conn.commit()
    
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    
    finally:
        conn.close()
        
    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    pass

if __name__ == '__main__':
    init_db()
    print("Auth Server Running!")
    app.run(debug=True, port=5000)