fetch('http://localhost:5000/api/notes')
    .then(response => response.json())
    .then(data => console.log("Backend says:", data.message))
    .catch(err => console.error("Engine failure:", err));