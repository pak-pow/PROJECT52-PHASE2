const noteList = document.getElementById('note-list');
const editorContainer = document.getElementById('editor-container');
const welcomeText = document.getElementById('welcome-text');
const titleInput = document.getElementById('note-title-input');
const markdownEditor = document.getElementById('markdown-editor');
const saveBtn = document.getElementById('save-note-btn');
const newNoteBtn = document.getElementById('new-note-btn');
const markdownPreview = document.getElementById('markdown-preview');

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
        
        welcomeText.classList.add('hidden');
        editorContainer.classList.remove('hidden');
    
        titleInput.value = data.filename;
        markdownEditor.value = data.content;
        
        markdownPreview.innerHTML = marked.parse(data.content);
    } catch (error) {
        console.error("Failed to load note:", error);
    }
}

saveBtn.addEventListener('click', async () => {
    const filename = titleInput.value.trim();
    const content = markdownEditor.value;

    if (!filename.endsWith('.md')) {
        alert("Filename must end with .md!");
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/api/notes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify({ filename: filename, content: content })
        });

        if (response.ok) {
            console.log(`Saved ${filename} to hard drive!`);
            loadNoteList();
        }
    } catch (error) {
        console.error("Failed to save:", error);
    }
});

newNoteBtn.addEventListener('click', () => {
    welcomeText.classList.add('hidden');
    editorContainer.classList.remove('hidden');
    titleInput.value = 'untitled.md';
    markdownEditor.value = '# New Note\n\nStart typing...';
});

markdownEditor.addEventListener('input', () => {
    const rawText = markdownEditor.value;
    markdownPreview.innerHTML = marked.parse(rawText);
});

loadNoteList();