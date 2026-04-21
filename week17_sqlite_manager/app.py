from flask import Flask, render_template, request, jsonify # type: ignore
from db_manager import DatabaseManager

app = Flask(__name__)
db = DatabaseManager("project52.db")

@app.route("/")
def home():
    return render_template("index.html")

