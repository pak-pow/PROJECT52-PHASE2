from flask import Flask, jsonify, request #type: ignore
from flask_cors import CORS #type: ignore
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

@app.route("/api/checkout", methods=["POST"])
def process_checkout():
    data = request.get_json()
    cart_items = data.get('cart', [])
    total_price = data.get('total_price', 0)

    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400

    total_items = sum(item['quantity'] for item in cart_items)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO orders (total_amount, total_items) VALUES (?, ?)',
            (total_price, total_items)
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Order placed successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port = 5000, debug=True)