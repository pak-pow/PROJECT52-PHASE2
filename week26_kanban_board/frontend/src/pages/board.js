export function renderBoard(container, boardId) {
    container.innerHTML = `
        <div style="padding: 2rem;">
            <h1><i data-lucide="trello"></i> Board Canvas (ID: ${boardId})</h1>
            <p style="color: var(--text-muted); margin-top: 1rem;">Drag and drop columns and cards will go here.</p>
            <a href="#" style="color: var(--accent); display: block; margin-top: 1rem;">&larr; Back to Dashboard</a>
        </div>
    `;
}