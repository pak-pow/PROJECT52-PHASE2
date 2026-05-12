from flask import Flask, jsonify #type: ignore
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

@app.route('/api/products', methods=['GET'])
def get_products():
    
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    
    product_list = [dict(row) for row in products]
    return jsonify({"products": product_list})

if __name__ == '__main__':
    app.run(port = 5000, debug=True)