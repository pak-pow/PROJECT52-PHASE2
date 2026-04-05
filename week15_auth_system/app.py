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
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()

    # Check if user exists AND if the password matches the hash
    # user[0] = id, user[1] = username, user[2] = password_hash
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
        
        # Generate the JWT 
        token = jwt.encode({
            'user_id': user[0],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'message': 'Login successful!', 'token': token}), 200

    # If the username doesn't exist OR the password was wrong:
    return jsonify({'error': 'Invalid username or password'}), 401

if __name__ == '__main__':
    init_db()
    print("Auth Server Running!")
    app.run(debug=True, port=5000)