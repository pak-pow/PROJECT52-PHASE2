from flask import Flask, jsonify

app = Flask(__name__)
@app.route('/', methods=['GET']) # type: ignore

def home():
    pass

if __name__ == '__main__':
    pass