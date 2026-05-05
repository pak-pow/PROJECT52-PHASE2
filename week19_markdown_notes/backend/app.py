from flask import Flask, jsonify, request # type: ignore
import os
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

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
    
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        
    return jsonify({"filename": filename, "content": content})

@app.route('/api/notes', methods=['POST'])
def save_note():
    data = request.get_json()
    filename = data.get('filename')
    content = data.get('content')
    
    filepath = os.path.join(DATA_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)
        
    return jsonify({"message": f"Successfully saved {filename}!"})

@app.route('/api/notes/<filename>', methods=['DELETE'])
def delete_notes(filename):
    filepath = os.path.join(DATA_DIR, filename)
    
    if not os.path.join(filepath):
        return jsonify({"error": "File not found"}), 404
    
    try: 
        os.remove(filepath)
        return jsonify({"message": f"Successfully deleted {filename}"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)