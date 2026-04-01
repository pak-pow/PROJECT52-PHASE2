// URL Api
const API_URL = 'http://127.0.0.1:5000/todos';

// grabbing the html elements so js can control
const todoList = document.getElementById('todoList');
const taskInput = document.getElementById("taskInput");
const addBtn = document.getElementById('addBtn');   
const filterBtns = document.querySelectorAll('.filter-btn');

// state variable, can be all, active, completed
let currentFilter = 'all';

function showToast(message, type = 'success'){
    const container = document.getElementById('toast-container');
    const toast = document.getElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    
    }, 3000)
}

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

        if (displayTodos.length === 0) {
            let emptyMessage = "✨ You're all caught up!";
            if (currentFilter === 'active') emptyMessage = "🌴 No active tasks. Time to chill!";
            if (currentFilter === 'completed') emptyMessage = "🚀 Get to work! No tasks completed yet.";

            const emptyLi = document.createElement('li');
            emptyLi.className = 'empty-state';
            emptyLi.innerHTML = `<span class="empty-text">${emptyMessage}</span>`;
            todoList.appendChild(emptyLi);
            
            return; 
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

            taskSpan.ondblclick = () => activateEditMode(li, taskSpan, todo)

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

function activateEditMode(li, taskSpan, todo) {
    // Create a new input box
    const editInput = document.createElement('input');
    editInput.type = 'text';
    editInput.value = todo.task;
    editInput.className = 'edit-input';

    // Swap the text with the input box
    li.insertBefore(editInput, taskSpan);
    li.removeChild(taskSpan);
    
    // Put the blinking cursor inside automatically
    editInput.focus(); 

    // When they click away (blur) or press Enter, save it!
    const saveEdit = () => {
        const newText = editInput.value.trim();
        if (newText === "") {
            showToast("Task cannot be empty!", "error");
            
            // Abort and reload original text
            loadTodos(); 
            return;
        }
        if (newText !== todo.task) {
            updateTaskText(todo.id, newText, todo.completed);
        } else {

            // No changes made, just redraw
            loadTodos(); 
        }
    };

    editInput.onblur = saveEdit;
    editInput.onkeypress = (e) => {
        if (e.key === 'Enter') editInput.blur();
    };
}

async function updateTaskText(id, newText, currentStatus) {
    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: newText, completed: currentStatus })
        });

        if (response.ok) {
            showToast("Task updated successfully!");
            loadTodos(); 
        }
    } catch (error) {
        showToast("Error updating task", "error");
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
        showToast("Please enter a task!", "error");
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
            showToast("Task added successfully!"); 
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
        showToast("Error updating task", "error");
    }
}

async function deleteTodo(id) {
    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE' 
        });

        if (response.ok) {
            showToast("Task deleted!", "error");
            loadTodos(); 
        }
    } catch (error) {
        showToast("Error deleting task", "error");
    }
}

addBtn.addEventListener('click', addTodo);
taskInput.addEventListener('keypress', function(event){
    if (event.key === 'Enter'){
        addTodo();
    }
});

loadTodos();