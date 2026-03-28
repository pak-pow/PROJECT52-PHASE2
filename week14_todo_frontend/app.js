// URL Api
const API_URL = 'http://127.0.0.1:5000/todos';

// grabbing the html elements so js can control
const todoList = document.getElementById('todoList');
const taskInput = document.getElementById("taskInput");
const addBtn = document.getElementById('addBtn');   

// GET / Read tasks
async function loadTodos(){
    try {
        // getting a get response from the local server
        const response = await fetch(API_URL);
        const data = await response.json();
        
        // clearing the list on the screen so we don't get duplicates
        todoList.innerHTML = '';

        data.todos.forEach(todo => {
            const li = document.createElement('li');
            li.textContent = todo.task;
            todoList.appendChild(li);
        });
    } catch (error) {
        console.error("Error connecting to the backend: ", error);
        todoList.innerHTML = "<li> Could not connect to the server. Is Python running?</li>";
    }
}

// POST / create tasks
async function addTodo() {
    const taskValue = taskInput.value.trim();

    if (taskValue === ""){
        alert("Please enter a task!");
        return;
    }

    try{
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ task: taskValue })
        });

        if (response.ok){
            taskInput.value = '';
            loadTodos();
        } else {
            const errorData = await response.json();
            alert(`Error: ${errorData.error}`)
        }
    } catch (error) {
        console.error("Error Adding Task:", error);
    }
}

addBtn.addEventListener('click', addTodo);
taskInput.addEventListener('keypress', function(event){
    if (event.key === 'Enter'){
        addTodo();
    }
});

loadTodos();