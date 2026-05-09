from flask import Flask, jsonify, request # type: ignore
from werkzeug.utils import secure_filename # type: ignore
import os
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
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
    
    safe_filename = secure_filename(filename)
    filepath = os.path.join(DATA_DIR, safe_filename)
    
    if not os.path.exists(filepath):
        return jsonify({"error": "File not Found"}), 404
    
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        
    return jsonify({"filename": safe_filename, "content": content})

@app.route('/api/notes', methods=['POST'])
def save_note():
    data = request.get_json()
    raw_filename = data.get('filename')
    content = data.get('content')
    
    filename = secure_filename(raw_filename)
    
    if not filename.endswith('.md'):
        return jsonify({"error": "Invalid file type. Must be .md"}), 400
        
    filepath = os.path.join(DATA_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)
        
    return jsonify({"message": f"Successfully saved {filename}!"})

@app.route('/api/notes/<filename>', methods=['DELETE'])
def delete_notes(filename):
    safe_filename = secure_filename(filename)
    filepath = os.path.join(DATA_DIR, safe_filename)
    
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    try: 
        os.remove(filepath)
        return jsonify({"message": f"Successfully deleted {safe_filename}"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)