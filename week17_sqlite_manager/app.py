from flask import Flask, render_template, request, jsonify # type: ignore
from db_manager import DatabaseManager

app = Flask(__name__)
db = DatabaseManager("project52.db")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/users", methods=['GET'])
def get_users():
    users = db.execute_read("SELECT * FROM users")
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')
    role = data.get('role')
    
    if not username or not role:
        return jsonify({"error": "Username and role are required"}), 400
        
    success = db.execute_write("INSERT INTO users (username, role) VALUES (?, ?)", (username, role))
    if success:
        return jsonify({"message": f"User {username} added!"}), 201
    else:
        return jsonify({"error": "Username might already exist."}), 400

@app.route('/api/users/<username>', methods=['DELETE'])
def delete_user(username):
    success = db.execute_write("DELETE FROM users WHERE username = ?", (username,))
    if success:
        return jsonify({"message": "User deleted!"}), 200
    else:
        return jsonify({"error": "Failed to delete user."}), 400

if __name__ == '__main__':
    # Initialize the table just in case it doesn't exist
    db.execute_write("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        role TEXT NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1
    );
    """)
    app.run(debug=True)