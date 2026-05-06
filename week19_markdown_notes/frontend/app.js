const noteList = document.getElementById('note-list');
const editorContainer = document.getElementById('editor-container');
const welcomeText = document.getElementById('welcome-text');
const titleInput = document.getElementById('note-title-input');
const markdownEditor = document.getElementById('markdown-editor');

async function loadNoteList() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/notes');
        const data = await response.json();
        
        noteList.innerHTML = '';
        
        data.notes.forEach(filename => {
            const li = document.createElement('li');
            li.textContent = filename;
            li.classList.add('note-item'); 
            
            li.addEventListener('click', () => loadNoteContent(filename));
            
            noteList.appendChild(li);
        });
    } catch (error) {
        console.error("Failed to connect to backend:", error);
    }
}

async function loadNoteContent(filename) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/notes/${filename}`);
        const data = await response.json();
        
        welcomeText.style.display = 'none';
        editorContainer.style.display = 'flex';
    
        titleInput.value = data.filename;
        markdownEditor.value = data.content;
        
    } catch (error) {
        console.error("Failed to load note:", error);
    }
}

loadNoteList();