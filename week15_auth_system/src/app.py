from functools import wraps
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

def token_required(f):
    @wraps(f)
    
    def decorated(*args, **kwargs):
        token = None
        
        # looking for token in headers
        if 'Authorization' in request.headers:
            
            # as the header comes in as 'Bearers <token_string>'
            # splitting in spaces just to grab the token part
            parts = request.headers['Authorization'].split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]
        
        # if no token then bye bye
        if not token:
            return jsonify({'error': "token is missing! Access Denied."}), 401
        
        # trying to decode
        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            
            # fetching the user from the data base
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id, username FROM users WHERE id = ?", (current_user_id,))
            current_user = c.fetchone()
            conn.close()
            
            if not current_user:
                return jsonify({'error': 'User not found!'}), 401
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired! Please log in again.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid!'}), 401
        
        # If everything is good it will they will be accepted
        return f(current_user, *args, **kwargs)
    
    return decorated

@app.route('/dashboard', methods=['GET'])
@token_required
def dashboard(current_user):

    # current_user[0] is the ID, current_user[1] is the username
    return jsonify({
        'message': f'Welcome to your private dashboard, {current_user[1]}!',
        'user_data': {
            'id': current_user[0],
            'username': current_user[1],
            'status': 'VIP Member'
        }
    }), 200
    

@app.route('/change-password', methods=['PUT'])
@token_required
def change_password(current_user):
    
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or new_password:
        return jsonify({'error': 'Old and new passwords are required'}), 400
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # grabbing the users current hashed password from the database
    c.execute("SELECT password_hash FROM users WHERE id = ?", (current_user[0],))
    stored_hash = c.fetchone()[0]
    
    # verifying the old password matches the stored hash
    if not bcrypt.checkpw(old_password.encode('utf-8'), stored_hash):
        conn.close()
        return jsonify({'error': 'Incorrect current password'}), 401
    
    # if it matches, hash the new password
    salt = bcrypt.gensalt()
    new_hashed = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    
    # update the database
    c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hashed, current_user[0]))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Password updated successfully!'}), 200

if __name__ == '__main__':
    init_db()
    print("Auth Server Running!")
    app.run(debug=True, port=5000)