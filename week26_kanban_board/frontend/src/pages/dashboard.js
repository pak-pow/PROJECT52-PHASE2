import { api } from '../api/kanban_api.js';
import { createBoardCard } from '../components/boardCard.js';
import { escapeHtml, openModal, closeModal, showToast } from '../utils/dom.js';
import { initDragAndDrop } from '../utils/drag.js';

export async function renderDashboard(container) {
    let activeEditBoardId = null;
    let selectedEditColor = '#6366f1';

    // 1. Initial Scaffold Layout with Modal markup
    container.innerHTML = `
        <div class="page-container">
            <div class="dashboard-header">
                <h1><i data-lucide="layout-dashboard" style="color: var(--accent);"></i> Your Workspaces</h1>
                <div class="dashboard-controls">
                    <div class="search-container">
                        <i data-lucide="search" class="search-icon"></i>
                        <input type="text" id="dashboard-search-input" class="form-input search-input" placeholder="Search boards...">
                    </div>
                    <button class="btn btn-primary" id="new-board-btn"><i data-lucide="plus"></i> New Board</button>
                </div>
            </div>
            
            <div id="boards-list-container">
                <p class="text-muted">Loading workspace boards...</p>
            </div>
        </div>

        <!-- Create Board Modal -->
        <div class="modal-overlay" id="create-board-modal">
            <div class="modal-dialog">
                <div class="modal-header">
                    <h2>Create New Board</h2>
                    <button class="btn btn-icon" id="close-modal-btn">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                
                <form id="create-board-form">
                    <div class="form-group">
                        <label class="form-label" for="board-title">Board Title *</label>
                        <input type="text" id="board-title" class="form-input" placeholder="e.g. Work Projects" required maxlength="100">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="board-desc">Description</label>
                        <textarea id="board-desc" class="form-input form-textarea" placeholder="Optional board summary..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Accent Color</label>
                        <div class="color-picker-grid" id="color-picker">
                            <div class="color-swatch selected" data-color="#6366f1" style="background-color: #6366f1;"></div>
                            <div class="color-swatch" data-color="#10b981" style="background-color: #10b981;"></div>
                            <div class="color-swatch" data-color="#3b82f6" style="background-color: #3b82f6;"></div>
                            <div class="color-swatch" data-color="#f59e0b" style="background-color: #f59e0b;"></div>
                            <div class="color-swatch" data-color="#ec4899" style="background-color: #ec4899;"></div>
                            <div class="color-swatch" data-color="#8b5cf6" style="background-color: #8b5cf6;"></div>
                        </div>
                    </div>

                    <div class="modal-actions">
                        <button type="button" class="btn" id="cancel-modal-btn">Cancel</button>
                        <button type="submit" class="btn btn-primary">Create Board</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Edit Board Modal -->
        <div class="modal-overlay" id="edit-board-modal">
            <div class="modal-dialog">
                <div class="modal-header">
                    <h2>Edit Board</h2>
                    <button class="btn btn-icon" id="close-edit-modal-btn">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                
                <form id="edit-board-form">
                    <div class="form-group">
                        <label class="form-label" for="edit-board-title">Board Title *</label>
                        <input type="text" id="edit-board-title" class="form-input" required maxlength="100">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="edit-board-desc">Description</label>
                        <textarea id="edit-board-desc" class="form-input form-textarea"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Accent Color</label>
                        <div class="color-picker-grid" id="edit-color-picker">
                            <div class="color-swatch" data-color="#6366f1" style="background-color: #6366f1;"></div>
                            <div class="color-swatch" data-color="#10b981" style="background-color: #10b981;"></div>
                            <div class="color-swatch" data-color="#3b82f6" style="background-color: #3b82f6;"></div>
                            <div class="color-swatch" data-color="#f59e0b" style="background-color: #f59e0b;"></div>
                            <div class="color-swatch" data-color="#ec4899" style="background-color: #ec4899;"></div>
                            <div class="color-swatch" data-color="#8b5cf6" style="background-color: #8b5cf6;"></div>
                        </div>
                    </div>

                    <div class="modal-actions">
                        <button type="button" class="btn" id="cancel-edit-modal-btn">Cancel</button>
                        <button type="submit" class="btn btn-primary">Save Changes</button>
                    </div>
                </form>
            </div>
        </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    // Helper to filter boards
    function filterBoards(query) {
        const q = query.toLowerCase().trim();
        const cards = container.querySelectorAll('.board-card');
        cards.forEach(card => {
            const title = card.querySelector('h3').textContent.toLowerCase();
            const desc = card.querySelector('p').textContent.toLowerCase();
            if (title.includes(q) || desc.includes(q)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    // 2. Fetch and render boards list
    async function loadBoards() {
        const listContainer = document.getElementById('boards-list-container');
        try {
            const boards = await api.getBoards();
            if (boards.length === 0) {
                listContainer.innerHTML = `
                    <div class="empty-state">
                        <i data-lucide="kanban"></i>
                        <p>No boards found. Create a board to get started!</p>
                    </div>
                `;
            } else {
                let html = '<div class="dashboard-grid">';
                boards.forEach(board => {
                    html += createBoardCard(board);
                });
                html += '</div>';
                listContainer.innerHTML = html;

                const dashboardGrid = listContainer.querySelector('.dashboard-grid');
                if (dashboardGrid) {
                    initDragAndDrop(
                        listContainer,
                        null,
                        null,
                        async ({ boardId, newPosition, revert }) => {
                            const searchInput = document.getElementById('dashboard-search-input');
                            if (searchInput && searchInput.value.trim() !== '') {
                                showToast('Reordering is disabled while search filter is active.', 'error');
                                revert();
                                return;
                            }

                            const cards = Array.from(dashboardGrid.children);
                            const updates = cards.map((card, idx) => {
                                card.dataset.position = idx;
                                return [parseInt(card.dataset.boardId), idx];
                            });

                            try {
                                await api.reorderBoards(updates);
                                showToast('Board order updated successfully', 'success');
                            } catch (err) {
                                showToast(`Failed to update board order: ${err.message}`, 'error');
                                revert();
                            }
                        }
                    );
                }
            }
            if (window.lucide) window.lucide.createIcons();
            attachBoardCardListeners();

            // Re-apply search filter if active
            const searchInput = document.getElementById('dashboard-search-input');
            if (searchInput && searchInput.value.trim() !== '') {
                filterBoards(searchInput.value);
            }
        } catch (error) {
            listContainer.innerHTML = `
                <div class="error-state">
                    <h3>Connection Error</h3>
                    <p>Could not connect to the server. Please verify your Python Flask app is running.</p>
                </div>
            `;
        }
    }

    // 3. Attach actions inside cards (like edit and delete)
    function attachBoardCardListeners() {
        // --- Edit Boards ---
        const editButtons = container.querySelectorAll('.edit-board-btn');
        editButtons.forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                const id = btn.getAttribute('data-id');
                activeEditBoardId = id;
                try {
                    const board = await api.getBoard(id);
                    document.getElementById('edit-board-title').value = board.title;
                    document.getElementById('edit-board-desc').value = board.description || '';
                    selectedEditColor = board.accent_color;
                    
                    const editColorPicker = document.getElementById('edit-color-picker');
                    editColorPicker.querySelectorAll('.color-swatch').forEach(swatch => {
                        if (swatch.getAttribute('data-color') === board.accent_color) {
                            swatch.classList.add('selected');
                        } else {
                            swatch.classList.remove('selected');
                        }
                    });
                    
                    openModal('edit-board-modal');
                } catch (error) {
                    showToast(`Failed to load board details: ${error.message}`, 'error');
                }
            });
        });

        // --- Delete Boards ---
        const deleteButtons = container.querySelectorAll('.delete-board-btn');
        deleteButtons.forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                const id = btn.getAttribute('data-id');
                const title = btn.getAttribute('data-title');
                if (confirm(`Are you sure you want to delete the board "${title}"? This will permanently delete all its columns and cards.`)) {
                    try {
                        await api.deleteBoard(id);
                        await loadBoards();
                    } catch (error) {
                        showToast(`Failed to delete board: ${error.message}`, 'error');
                    }
                }
            });
        });
    }

    // 4. Modal Event Listeners
    // --- Create Board Modal ---
    const openBtn = document.getElementById('new-board-btn');
    const closeBtn = document.getElementById('close-modal-btn');
    const cancelBtn = document.getElementById('cancel-modal-btn');
    const form = document.getElementById('create-board-form');
    const colorPicker = document.getElementById('color-picker');
    let selectedColor = '#6366f1';

    openBtn.addEventListener('click', () => {
        form.reset();
        selectedColor = '#6366f1';
        colorPicker.querySelectorAll('.color-swatch').forEach(swatch => {
            if (swatch.getAttribute('data-color') === '#6366f1') {
                swatch.classList.add('selected');
            } else {
                swatch.classList.remove('selected');
            }
        });
        openModal('create-board-modal');
    });

    const closeActions = [closeBtn, cancelBtn];
    closeActions.forEach(btn => {
        btn.addEventListener('click', () => closeModal('create-board-modal'));
    });

    colorPicker.addEventListener('click', (e) => {
        const swatch = e.target.closest('.color-swatch');
        if (swatch) {
            colorPicker.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
            swatch.classList.add('selected');
            selectedColor = swatch.getAttribute('data-color');
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const titleInput = document.getElementById('board-title');
        const descInput = document.getElementById('board-desc');
        
        try {
            await api.createBoard({
                title: titleInput.value.trim(),
                description: descInput.value.trim(),
                accent_color: selectedColor
            });
            closeModal('create-board-modal');
            await loadBoards();
        } catch (error) {
            showToast(`Error creating board: ${error.message}`, 'error');
        }
    });

    // --- Edit Board Modal ---
    const closeEditBtn = document.getElementById('close-edit-modal-btn');
    const cancelEditBtn = document.getElementById('cancel-edit-modal-btn');
    const editForm = document.getElementById('edit-board-form');
    const editColorPicker = document.getElementById('edit-color-picker');

    const closeEditActions = [closeEditBtn, cancelEditBtn];
    closeEditActions.forEach(btn => {
        btn.addEventListener('click', () => closeModal('edit-board-modal'));
    });

    editColorPicker.addEventListener('click', (e) => {
        const swatch = e.target.closest('.color-swatch');
        if (swatch) {
            editColorPicker.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
            swatch.classList.add('selected');
            selectedEditColor = swatch.getAttribute('data-color');
        }
    });

    editForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const titleInput = document.getElementById('edit-board-title');
        const descInput = document.getElementById('edit-board-desc');
        
        try {
            await api.updateBoard(activeEditBoardId, {
                title: titleInput.value.trim(),
                description: descInput.value.trim(),
                accent_color: selectedEditColor
            });
            closeModal('edit-board-modal');
            await loadBoards();
        } catch (error) {
            showToast(`Error updating board: ${error.message}`, 'error');
        }
    });

    // Attach search input listener
    const searchInput = document.getElementById('dashboard-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            filterBoards(e.target.value);
        });
    }

    // Initial load
    await loadBoards();
}