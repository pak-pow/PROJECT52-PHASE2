import { api } from '../api/kanban_api.js';
import { createBoardCard } from '../components/boardCard.js';
import { escapeHtml, openModal, closeModal } from '../utils/dom.js';

export async function renderDashboard(container) {
    // 1. Initial Scaffold Layout with Modal markup
    container.innerHTML = `
        <div class="page-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <h1><i data-lucide="layout-dashboard" style="color: var(--accent);"></i> Your Workspaces</h1>
                <button class="btn btn-primary" id="new-board-btn"><i data-lucide="plus"></i> New Board</button>
            </div>
            
            <div id="boards-list-container">
                <p style="color: var(--text-muted);">Loading workspace boards...</p>
            </div>
        </div>

        <!-- Create Board Modal -->
        <div class="modal-overlay" id="create-board-modal">
            <div class="modal-dialog">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                    <h2 style="font-size: 1.25rem;">Create New Board</h2>
                    <button class="btn btn-icon" id="close-modal-btn" style="border: none; background: transparent;">
                        <i data-lucide="x"></i>
                    </button>
                </div>
                
                <form id="create-board-form">
                    <div class="form-group">
                        <label class="form-label" for="board-title">Board Title *</label>
                        <input type="text" id="board-title" class="form-input" placeholder="e.g. Work Projects" required max-length="100">
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

                    <div style="display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 2rem;">
                        <button type="button" class="btn" id="cancel-modal-btn">Cancel</button>
                        <button type="submit" class="btn btn-primary">Create Board</button>
                    </div>
                </form>
            </div>
        </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    // 2. Fetch and render boards list
    async function loadBoards() {
        const listContainer = document.getElementById('boards-list-container');
        try {
            const boards = await api.getBoards();
            if (boards.length === 0) {
                listContainer.innerHTML = `
                    <div style="text-align: center; padding: 4rem 2rem; border: 1px dashed var(--border-color); border-radius: var(--radius-md);">
                        <i data-lucide="kanban" style="width: 48px; height: 48px; color: var(--text-muted); margin-bottom: 1rem;"></i>
                        <p style="color: var(--text-muted); font-size: 1rem;">No boards found. Create a board to get started!</p>
                    </div>
                `;
            } else {
                let html = '<div class="dashboard-grid">';
                boards.forEach(board => {
                    html += createBoardCard(board);
                });
                html += '</div>';
                listContainer.innerHTML = html;
            }
            if (window.lucide) window.lucide.createIcons();
            attachBoardCardListeners();
        } catch (error) {
            listContainer.innerHTML = `
                <div style="padding: 2rem; border: 1px solid var(--danger); border-radius: var(--radius-md); background: rgba(239,68,68,0.05);">
                    <h3 style="color: var(--danger); margin-bottom: 0.5rem;">Connection Error</h3>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">Could not connect to the server. Please verify your Python Flask app is running.</p>
                </div>
            `;
        }
    }

    // 3. Attach actions inside cards (like delete)
    function attachBoardCardListeners() {
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
                        alert(`Failed to delete board: ${error.message}`);
                    }
                }
            });
        });
    }

    // 4. Modal Event Listeners
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

    // Color Swatch Picker listener
    colorPicker.addEventListener('click', (e) => {
        const swatch = e.target.closest('.color-swatch');
        if (swatch) {
            colorPicker.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
            swatch.classList.add('selected');
            selectedColor = swatch.getAttribute('data-color');
        }
    });

    // Form submit action
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
            alert(`Error creating board: ${error.message}`);
        }
    });

    // Initial load
    await loadBoards();
}