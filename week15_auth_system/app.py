from flask import Flask, request, jsonify   #type: ignore
from flask_cors import CORS                 #type: ignore
import bcrypt                               #type: ignore
import sqlite3                              #type: ignore

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'super-secret-project52-key'
DB_NAME = 'users.db'

def init_db():
    pass

@app.route('/register', methods=['POST'])
def register():
    pass

if __name__ == '__main__':
    init_db()
    print("Auth Server Running!")
    app.run(debug=True, port=5000)