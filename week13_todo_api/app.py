from flask import Flask, jsonify, request

todos = [
    {"id": 1, "task": "Learn Flask", "completed": True},
    {"id": 2, "task": "Build GET and POST endpoints", "completed":False}
]

app = Flask(__name__)
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
    pass


if __name__ == '__main__':
    print("Starting TODO Backend Server")
    app.run(debug=True, port=5000)