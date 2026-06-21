import { api } from '../api/kanban_api.js';
import { createColumnHTML } from '../components/column.js';
import { createCardHTML } from '../components/card.js';
import { escapeHtml, openModal, closeModal } from '../utils/dom.js';
import { initDragAndDrop } from '../utils/drag.js';

export async function renderBoard(container, boardId) {
    let boardData = null;
    let activeAddCardColumnId = null;
    let activeEditCardId = null;

    // 1. Initial Scaffold Layout with Modal markups
    container.innerHTML = `
        <!-- Board Header Sticky Nav -->
        <div class="board-header" id="board-header-section">
            <div>
                <a href="#" style="color: var(--text-muted); text-decoration: none; font-size: 0.875rem; display: inline-flex; align-items: center; gap: 0.25rem; margin-bottom: 0.25rem;">
                    <i data-lucide="chevron-left" style="width: 16px; height: 16px;"></i> Back to Dashboard
                </a>
                <h1 id="board-title-display" style="font-size: 1.5rem; margin: 0;">Loading Board...</h1>
                <p id="board-desc-display" style="color: var(--text-muted); font-size: 0.875rem; margin-top: 0.25rem;"></p>
            </div>
            <div style="display: flex; gap: 0.75rem;">
                <button class="btn btn-primary" id="add-column-btn"><i data-lucide="plus"></i> Add Column</button>
            </div>
        </div>

        <!-- Board Canvas horizontal scrolling layout -->
        <div class="board-canvas-wrapper">
            <div class="board-canvas" id="board-columns-list">
                <p style="color: var(--text-muted);">Loading columns and cards...</p>
            </div>
        </div>

        <!-- Add Column Modal -->
        <div class="modal-overlay" id="create-column-modal">
            <div class="modal-dialog">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                    <h2 style="font-size: 1.25rem;">Create New Column</h2>
                    <button class="btn btn-icon" id="close-column-modal-btn" style="border: none; background: transparent;">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <form id="create-column-form">
                    <div class="form-group">
                        <label class="form-label" for="column-title">Column Title *</label>
                        <input type="text" id="column-title" class="form-input" placeholder="e.g. In Progress" required maxlength="100">
                    </div>
                    <div style="display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 2rem;">
                        <button type="button" class="btn" id="cancel-column-modal-btn">Cancel</button>
                        <button type="submit" class="btn btn-primary">Create Column</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Add Card Modal -->
        <div class="modal-overlay" id="create-card-modal">
            <div class="modal-dialog">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                    <h2 style="font-size: 1.25rem;">Create New Task</h2>
                    <button class="btn btn-icon" id="close-card-modal-btn" style="border: none; background: transparent;">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <form id="create-card-form">
                    <div class="form-group">
                        <label class="form-label" for="card-title">Task Title *</label>
                        <input type="text" id="card-title" class="form-input" placeholder="e.g. Design Mockups" required maxlength="150">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="card-desc">Description</label>
                        <textarea id="card-desc" class="form-input form-textarea" placeholder="Describe the task..."></textarea>
                    </div>
                    <div style="display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 2rem;">
                        <button type="button" class="btn" id="cancel-card-modal-btn">Cancel</button>
                        <button type="submit" class="btn btn-primary">Create Task</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Edit Card Modal -->
        <div class="modal-overlay" id="edit-card-modal">
            <div class="modal-dialog">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                    <h2 style="font-size: 1.25rem;">Edit Task</h2>
                    <button class="btn btn-icon" id="close-edit-modal-btn" style="border: none; background: transparent;">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                <form id="edit-card-form">
                    <div class="form-group">
                        <label class="form-label" for="edit-card-title">Task Title *</label>
                        <input type="text" id="edit-card-title" class="form-input" required maxlength="150">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="edit-card-desc">Description</label>
                        <textarea id="edit-card-desc" class="form-input form-textarea"></textarea>
                    </div>
                    <div style="display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 2rem;">
                        <button type="button" class="btn" id="cancel-edit-modal-btn">Cancel</button>
                        <button type="submit" class="btn btn-primary">Save Changes</button>
                    </div>
                </form>
            </div>
        </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    // 2. Fetch Board Details and Hydrate Columns & Cards
    async function loadBoard() {
        const columnsList = document.getElementById('board-columns-list');
        const boardTitle = document.getElementById('board-title-display');
        const boardDesc = document.getElementById('board-desc-display');

        try {
            boardData = await api.getBoard(boardId);
            
            // Set dynamic accent styling
            document.documentElement.style.setProperty('--accent', boardData.accent_color);
            // Derive a slightly darker hover accent
            document.documentElement.style.setProperty('--accent-hover', boardData.accent_color + 'dd');

            boardTitle.innerHTML = `<i data-lucide="layout" style="color: var(--accent);"></i> ${escapeHtml(boardData.title)}`;
            boardDesc.textContent = boardData.description || 'No description provided for this board.';

            if (boardData.columns.length === 0) {
                columnsList.innerHTML = `
                    <div style="text-align: center; margin: auto; padding: 4rem 2rem;">
                        <i data-lucide="columns" style="width: 48px; height: 48px; color: var(--text-muted); margin-bottom: 1rem;"></i>
                        <p style="color: var(--text-muted); font-size: 1rem;">No columns found. Create one to start organizing cards!</p>
                    </div>
                `;
            } else {
                let columnsHtml = '';
                boardData.columns.forEach(col => {
                    const cardsHtml = (col.cards || [])
                        .map(card => createCardHTML(card))
                        .join('');
                    columnsHtml += createColumnHTML(col, cardsHtml);
                });
                columnsList.innerHTML = columnsHtml;
            }
            
            if (window.lucide) window.lucide.createIcons();
            attachCanvasListeners();

        } catch (error) {
            columnsList.innerHTML = `
                <div style="margin: auto; padding: 2rem; border: 1px solid var(--danger); border-radius: var(--radius-md); background: rgba(239,68,68,0.05); max-width: 500px;">
                    <h3 style="color: var(--danger); margin-bottom: 0.5rem;">Failed to load Board</h3>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">The board does not exist or the server could not be reached.</p>
                </div>
            `;
        }
    }

    // 3. Attach Actions & Events inside Columns/Cards
    function attachCanvasListeners() {
        // --- Inline Rename Columns ---
        const inputs = container.querySelectorAll('.column-title-input');
        inputs.forEach(input => {
            input.addEventListener('blur', async () => {
                const id = input.getAttribute('data-id');
                const newVal = input.value.trim();
                const oldVal = input.getAttribute('data-original-val');
                
                if (newVal === '') {
                    input.value = oldVal;
                    return;
                }
                
                if (newVal !== oldVal) {
                    try {
                        await api.updateColumn(id, newVal);
                        input.setAttribute('data-original-val', newVal);
                    } catch (error) {
                        alert(`Failed to rename column: ${error.message}`);
                        input.value = oldVal;
                    }
                }
            });
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    input.blur();
                }
            });
        });

        // --- Delete Columns ---
        const deleteColBtns = container.querySelectorAll('.delete-column-btn');
        deleteColBtns.forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.getAttribute('data-id');
                const title = btn.getAttribute('data-title');
                if (confirm(`Delete the column "${title}"? All cards inside it will be permanently deleted.`)) {
                    try {
                        await api.deleteColumn(id);
                        await loadBoard();
                    } catch (error) {
                        alert(`Failed to delete column: ${error.message}`);
                    }
                }
            });
        });

        // --- Create Card Trigger ---
        const addCardBtns = container.querySelectorAll('.add-card-btn');
        addCardBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                activeAddCardColumnId = btn.getAttribute('data-column-id');
                document.getElementById('create-card-form').reset();
                openModal('create-card-modal');
            });
        });

        // --- Edit Card Trigger ---
        const editCardBtns = container.querySelectorAll('.edit-card-btn');
        editCardBtns.forEach(btn => {
            btn.addEventListener('click', async () => {
                activeEditCardId = btn.getAttribute('data-id');
                try {
                    const card = await api.getCard(activeEditCardId);
                    document.getElementById('edit-card-title').value = card.title;
                    document.getElementById('edit-card-desc').value = card.description || '';
                    openModal('edit-card-modal');
                } catch (error) {
                    alert(`Failed to fetch card details: ${error.message}`);
                }
            });
        });

        // --- Delete Cards ---
        const deleteCardBtns = container.querySelectorAll('.delete-card-btn');
        deleteCardBtns.forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.getAttribute('data-id');
                const title = btn.getAttribute('data-title');
                if (confirm(`Delete task "${title}"?`)) {
                    try {
                        await api.deleteCard(id);
                        await loadBoard();
                    } catch (error) {
                        alert(`Failed to delete card: ${error.message}`);
                    }
                }
            });
        });
    }

    // 4. Modal Event Listeners
    // --- Column Modal ---
    document.getElementById('add-column-btn').addEventListener('click', () => {
        document.getElementById('create-column-form').reset();
        openModal('create-column-modal');
    });
    document.getElementById('close-column-modal-btn').addEventListener('click', () => closeModal('create-column-modal'));
    document.getElementById('cancel-column-modal-btn').addEventListener('click', () => closeModal('create-column-modal'));
    
    document.getElementById('create-column-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const titleInput = document.getElementById('column-title');
        try {
            await api.createColumn(boardId, titleInput.value.trim());
            closeModal('create-column-modal');
            await loadBoard();
        } catch (error) {
            alert(`Error creating column: ${error.message}`);
        }
    });

    // --- Card Modal (Add) ---
    document.getElementById('close-card-modal-btn').addEventListener('click', () => closeModal('create-card-modal'));
    document.getElementById('cancel-card-modal-btn').addEventListener('click', () => closeModal('create-card-modal'));
    
    document.getElementById('create-card-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const titleInput = document.getElementById('card-title');
        const descInput = document.getElementById('card-desc');
        try {
            await api.createCard(activeAddCardColumnId, {
                title: titleInput.value.trim(),
                description: descInput.value.trim()
            });
            closeModal('create-card-modal');
            await loadBoard();
        } catch (error) {
            alert(`Error creating card: ${error.message}`);
        }
    });

    // --- Card Modal (Edit) ---
    document.getElementById('close-edit-modal-btn').addEventListener('click', () => closeModal('edit-card-modal'));
    document.getElementById('cancel-edit-modal-btn').addEventListener('click', () => closeModal('edit-card-modal'));
    
    document.getElementById('edit-card-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const titleInput = document.getElementById('edit-card-title');
        const descInput = document.getElementById('edit-card-desc');
        try {
            await api.updateCard(activeEditCardId, {
                title: titleInput.value.trim(),
                description: descInput.value.trim()
            });
            closeModal('edit-card-modal');
            await loadBoard();
        } catch (error) {
            alert(`Error updating card: ${error.message}`);
        }
    });

    // 5. Drag and Drop Hook integration
    initDragAndDrop({
        onCardMove: async (cardId, targetColumnId, targetPosition) => {
            try {
                // Persistent move endpoint trigger
                await api.moveCard(cardId, targetColumnId, targetPosition);
                // Refresh board content to guarantee positions/rendering alignment
                await loadBoard();
            } catch (error) {
                console.error(`Move failed:`, error);
                alert(`Could not save card placement: ${error.message}`);
                // Hard reload to roll back local DOM changes to last synced DB state
                await loadBoard();
            }
        }
    });

    // Initial Load
    await loadBoard();
}