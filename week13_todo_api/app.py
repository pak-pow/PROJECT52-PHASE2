import os
import json

from flask import Flask, jsonify, request
from flask_cors import CORS #type: ignore

app = Flask(__name__)
CORS(app)

# Permanent storage setup
FILE_PATH = "todos.json"

def load_todos():
    """
    reading tasks from json file
    and if file is nowhere to be seen it will return 
    an empty list
    """
    
    if not os.path.exists(FILE_PATH):
        return []
    
    with open(FILE_PATH, "r") as file:
        return json.load(file)
    
def save_todos(todos):
    """
    The function `save_todos` saves a list of todos to a file in JSON format with an indent of 4 spaces.
    
    :param todos: The `todos` parameter is a list of tasks or to-dos that need to be saved to a file.
    The `save_todos` function takes this list of tasks and writes it to a file in JSON format with an
    indentation of 4 spaces
    """
    with open(FILE_PATH, "w") as file:
        json.dump(todos, file, indent=4)

# API Endpoints
@app.route('/', methods=['GET']) # type: ignore
def home():
    return jsonify({
        "status": "success", 
        "message": "Welcome to the TODO API!",
        "version": "1.0"
    })

@app.route("/todos", methods=["GET"])
def get_todos():
    todos = load_todos()
    return jsonify({"todos": todos})

@app.route("/todos", methods=['POST'])
def add_todos():
    todos = load_todos()
    incoming_data = request.get_json()

    if not incoming_data or "task" not in incoming_data or incoming_data["task"].strip() == "":
        return jsonify({"error": "Task cannot be empty"}), 400

    new_id = 1 if len(todos) == 0 else max(t["id"] for t in todos) + 1
    new_todo = {
        "id": new_id,
        "task": incoming_data["task"],
        "completed": False
    }

    todos.append(new_todo)
    save_todos(todos)
    return jsonify(new_todo), 201


@app.route("/todos/<int:todo_id>", methods=["PUT"]) #type: ignore
def update_todo(todo_id):
    todos = load_todos()
    incoming_data = request.get_json()
    
    for todo in todos:
        if todo["id"] == todo_id:
            
            if "task" in incoming_data and incoming_data["task"].strip() == "":
                return jsonify({"error": "Updated task cannot be empty!"}), 400
            
            todo["task"] = incoming_data.get("task", todo["task"])
            todo["completed"] = incoming_data.get("completed", todo["completed"])
            
            save_todos(todos)
            return jsonify({"message": "Todo updated successfully", "todo": todo})
        
    return jsonify({"error": "Todo not found"}), 404

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todos = load_todos()
    
    if not any(todo["id"] == todo_id for todo in todos):
        return jsonify({"error": "Todo not found, cannot delete."}), 404
    
    todos = [todo for todo in todos if todo["id"] != todo_id]
    save_todos(todos)
    
    return jsonify({"message": f"Todo {todo_id} deleted successfully!"})

if __name__ == '__main__':
    print("Starting TODO Backend Server")
    app.run(debug=True, port=5000)