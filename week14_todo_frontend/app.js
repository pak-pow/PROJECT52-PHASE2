const API_URL = 'http://127.0.0.1:5000/todos';
const todoList = document.getElementById('todoList');

asynch function loadTodos(){

    try {

        // getting a get response from the local server
        const response = await fetch(API_URL);
        const data = await response.json();
        
        // clearing the list on the screen so we don't get duplicates
        todoList.innerHTML = '';

        data.todos.forEach(todo => {
            const li = document.createElement('li');
        });


    }

}

loadTodos();