const noteList = document.getElementById('note-list');
async function loadNoteList() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/notes');
        const data = await response.json();
        noteList.innerHTML = '';
        data.notes.forEach(filename => {
            const li = document.createElement('li');
            li.textContent = filename;
            li.classList.add('note-item'); 
            noteList.appendChild(li);
        });
    } catch (error) {
        console.error("Failed to connect to backend:", error);
    }
}

loadNoteList();