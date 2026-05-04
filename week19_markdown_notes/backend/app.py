from flask import Flask, jsonify # type: ignore
app = Flask(__name__)

@app.after_request
def add_cors(response):
    pass

@app.route('/api/notes', methods=['GET'])
def get_notes():
    pass