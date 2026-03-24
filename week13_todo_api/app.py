from flask import Flask, jsonify, request
from flask_cors import CORS 

todos = [
    {"id": 1, "task": "Learn Flask", "completed": True},
    {"id": 2, "task": "Build GET and POST endpoints", "completed":False}
]

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET']) # type: ignore

def home():
    response_data = {
        "status": "success",
        "message": "TODO App is UP",
        "version": "1.0"
    }

    return jsonify(response_data)

@app.route("/todos", methods=["GET"])
def get_todos():
    return jsonify({"todos": todos})

@app.route("/todos", methods=['POST'])
def add_todos():
    incoming_data = request.get_json()

    new_todo = {
        "id": len(todos) + 1,
        "task": incoming_data["task"],
        "completed": False
    }

    todos.append(new_todo)
    return jsonify(new_todo), 201


@app.route("/todos/<int:todo_id>", methods=["PUT"]) #type: ignore
def update_todo(todo_id):
    incoming_data = request.get_json()
    
    for todo in todos:
        if todo["id"] == todo_id:
            todo["task"] = incoming_data.get("task", todo["task"])
            todo["completed"] = incoming_data.get("completed", todo["completed"])
            return jsonify({"message": "Todo updated successfully", "todo": todo})
        
    return jsonify({"error": "Todo not found"}), 404

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos 
    todos = [todo for todo in todos if todo["id"] != todo_id]
    
    return jsonify({"message": f"Todo {todo_id} deleted successfully!"})

if __name__ == '__main__':
    print("Starting TODO Backend Server")
    app.run(debug=True, port=5000)