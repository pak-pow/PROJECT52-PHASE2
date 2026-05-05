from flask import Flask, jsonify, request # type: ignore
import os
app = Flask(__name__)

DATA_DIR = "data"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/notes', methods=['GET'])
def list_notes():
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith('.md')]
        return jsonify({"notes": files})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notes/<filename>', methods=['GET'])
def read_notes(filename):
    filepath = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(filepath):
        return jsonify({"error": "File not Found"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)