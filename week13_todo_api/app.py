from flask import Flask, jsonify

app = Flask(__name__)
@app.route('/', methods=['GET']) # type: ignore

def home():
    response_data = {
        "status": "success",
        "message": "TODO App is UP",
        "version": "1.0"
    }
    
    return jsonify(response_data)

if __name__ == '__main__':
    print("Starting TODO Backend Server")
    app.run(debug=True, port=5000)