from flask import Flask, jsonify # type: ignore
app = Flask(__name__)

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/notes', methods=['GET'])
def get_notes():
    return jsonify({
        "message": "Hello from file system!"
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)