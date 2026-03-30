// URL Api
const API_URL = 'http://127.0.0.1:5000/todos';

// grabbing the html elements so js can control
const todoList = document.getElementById('todoList');
const taskInput = document.getElementById("taskInput");
const addBtn = document.getElementById('addBtn');   
const filterBtns = document.querySelectorAll('.filter-btn');

// state variable, can be all, active, completed
let currentFilter = 'all';

// GET / Read tasks
async function loadTodos(){
    try {
        // getting a get response from the local server
        const response = await fetch(API_URL);
        const data = await response.json();
        
        // clearing the list on the screen so we don't get duplicates
        todoList.innerHTML = '';
        
        let displayTodos = data.todos;
        
        if(currentFilter === 'active') {
            displayTodos = data.todos.filter(todo => todo.completed === false);
        
        } else if (currentFilter === 'completed') {
            displayTodos = data.todos.filter(todo => todo.completed === true);
        }

        displayTodos.forEach(todo => {
            const li = document.createElement('li');

            if (todo.completed){
                li.classList.add('completed');
            }
            
            // Create the clickable text (PUT trigger)
            const taskSpan = document.createElement('span');
            taskSpan.className = 'task-text';
            taskSpan.textContent = todo.task;

            // When clicked, send the ID, the name, and the current status to be flipped
            taskSpan.onclick = () => toggleComplete(todo.id, todo.task, todo.completed);

            // Create the delete button (DELETE trigger)
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.textContent = '❌';

            // Send the ID to be destroyed
            deleteBtn.onclick = () => deleteTodo(todo.id); 

            // Assemble the HTML
            li.appendChild(taskSpan);
            li.appendChild(deleteBtn);
            todoList.appendChild(li);
        });
    } catch (error) {
        console.error("Error connecting to the backend: ", error);
        todoList.innerHTML = "<li> Could not connect to the server. Is Python running?</li>";
    }
}

filterBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        // Remove the 'active' purple highlight from all buttons
        filterBtns.forEach(b => b.classList.remove('active'));
        
        // Add the 'active' highlight to the exact button we just clicked
        e.target.classList.add('active');
        
        // Update our state variable based on the button's text (All, Active, Completed)
        currentFilter = e.target.textContent.toLowerCase();
        
        // Redraw the list using the new filter!
        loadTodos();
    });
});


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

async function toggleComplete(id, currentTaskName, currentStatus) {
    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({
                task: currentTaskName,
                completed: !currentStatus
            })
        });

        if (response.ok){
            loadTodos();
        }
    } catch (error){
        console.error("Error updating task: ", error);
    }
}

async function deleteTodo(id) {
    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE' 
        });

        if (response.ok) {
            loadTodos(); 
        }
    } catch (error) {
        console.error("Error deleting task:", error);
    }
}

addBtn.addEventListener('click', addTodo);
taskInput.addEventListener('keypress', function(event){
    if (event.key === 'Enter'){
        addTodo();
    }
});

loadTodos();