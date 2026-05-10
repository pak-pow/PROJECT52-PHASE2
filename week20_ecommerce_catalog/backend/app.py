from flask import Flask, jsonify #type: ignore
from flask_cors import CORS #type: ignore

app = Flask(__name__)
CORS(app)

PRODUCTS = [
    {"id": 1, "name": "Sony WH-1000XM5", "category": "Electronics", "price": 348.00, "image": "🎧"},
    {"id": 2, "name": "Mechanical Keyboard", "category": "Electronics", "price": 120.50, "image": "⌨️"},
    {"id": 3, "name": "Ergonomic Office Chair", "category": "Furniture", "price": 299.99, "image": "🪑"},
    {"id": 4, "name": "Ceramic Coffee Mug", "category": "Home", "price": 18.00, "image": "☕"},
    {"id": 5, "name": "Python Crash Course", "category": "Books", "price": 25.99, "image": "📘"},
    {"id": 6, "name": "Gaming Mouse", "category": "Electronics", "price": 60.00, "image": "🖱️"}
]

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify({"products": PRODUCTS})

if __name__ == '__main__':
    app.run(port = 5000, debug=True)