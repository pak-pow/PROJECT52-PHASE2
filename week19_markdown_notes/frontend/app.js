const noteList = document.getElementById('note-list');
const editorContainer = document.getElementById('editor-container');
const welcomeText = document.getElementById('welcome-text');
const titleInput = document.getElementById('note-title-input');
const markdownEditor = document.getElementById('markdown-editor');
const saveBtn = document.getElementById('save-note-btn');
const newNoteBtn = document.getElementById('new-note-btn');
const markdownPreview = document.getElementById('markdown-preview');
const deleteBtn = document.getElementById('delete-note-btn');
const toastContainer = document.getElementById('toast-container');

const API_BASE = 'http://127.0.0.1:5000/api/notes';
let currentNote = null;
let isDirty = false;

marked.setOptions({
    breaks: true, 
    gfm: true
});

function checkUnsavedChanges() {
    if (isDirty) {
        return confirm("You have unsaved changes. Are you sure you want to leave without saving?");
    }
    return true; 
}

function showToast(message, isError = false){
    const toast = document.createElement('div');
    toast.classList.add('toast');
    if (isError) toast.classList.add('error');
    toast.textContent = message;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('fade-out');
        toast.addEventListener('animationend', () => toast.remove());
    }, 3000);
}

function highlightActiveNote(filename) {
    const items = document.querySelectorAll('.note-item');
    items.forEach(item => {
        if (item.textContent === filename) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

async function loadNoteList() {
    try {
        const response = await fetch(API_BASE);
        const data = await response.json();
        
        noteList.innerHTML = '';
        
        data.notes.forEach(filename => {
            const li = document.createElement('li');
            li.textContent = filename;
            li.classList.add('note-item'); 
            
            li.addEventListener('click', () => {
                if (checkUnsavedChanges()) {
                    loadNoteContent(filename);
                }
            });
            
            noteList.appendChild(li);
        });

        if (currentNote) highlightActiveNote(currentNote);
    } catch (error) {
        console.error("Failed to connect to backend:", error);
    }
}

async function loadNoteContent(filename) {
    try {
        const response = await fetch(`${API_BASE}/${filename}`);
        const data = await response.json();
        
        welcomeText.classList.add('hidden');
        editorContainer.classList.remove('hidden');
    
        titleInput.value = data.filename;
        markdownEditor.value = data.content;
        markdownPreview.innerHTML = marked.parse(data.content);

        currentNote = data.filename;
        isDirty = false;
        highlightActiveNote(currentNote);
    } catch (error) {
        console.error("Failed to load note:", error);
    }
}

markdownEditor.addEventListener('input', () => {
    isDirty = true;
    const rawText = markdownEditor.value;
    markdownPreview.innerHTML = marked.parse(rawText);
});
titleInput.addEventListener('input', () => isDirty = true);


saveBtn.addEventListener('click', async () => {
    const filename = titleInput.value.trim();
    const content = markdownEditor.value;

    if (!filename) {
        showToast("Filename cannot be empty!", true);
        return;
    }
    if (!filename.endsWith('.md')) {
        showToast("Filename must end with .md!", true);
        return;
    }

    try {
        const response = await fetch(API_BASE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename, content })
        });

        if (response.ok) {
            isDirty = false;
            currentNote = filename;
            showToast(`Successfully saved ${filename}`);
            loadNoteList(); 
        }
    } catch (error) {
        showToast("Failed to connect to server.", true);
    }
});

newNoteBtn.addEventListener('click', () => {
    if (!checkUnsavedChanges()) return;
    
    currentNote = null;
    isDirty = false;
    
    welcomeText.classList.add('hidden');
    editorContainer.classList.remove('hidden');
    titleInput.value = 'untitled.md';
    markdownEditor.value = '# New Note\n\nStart typing...';
    markdownPreview.innerHTML = marked.parse(markdownEditor.value);
    
    highlightActiveNote(null);
});

deleteBtn.addEventListener('click', async () => {
    const filename = titleInput.value.trim();
    if (!filename) return;

    if (!confirm(`Are you sure you want to permanently delete ${filename}?`)) {
        return; 
    }

    try {
        const response = await fetch(`${API_BASE}/${filename}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast(`Deleted ${filename}`);
            currentNote = null;
            isDirty = false;
            
            loadNoteList(); 
            editorContainer.classList.add('hidden');
            welcomeText.classList.remove('hidden');
        }
    } catch (error) {
        showToast("Failed to delete note.", true);
    }
});

document.addEventListener('keydown', (e) => {
    const isModifierPressed = e.ctrlKey || e.metaKey;

    if (isModifierPressed && e.key.toLowerCase() === 's') {
        e.preventDefault(); 
        if (!editorContainer.classList.contains('hidden')) {
            saveBtn.click(); 
        }
    }

    if (isModifierPressed && e.key.toLowerCase() === 'n') {
        e.preventDefault();
        newNoteBtn.click();
    }
});

loadNoteList();