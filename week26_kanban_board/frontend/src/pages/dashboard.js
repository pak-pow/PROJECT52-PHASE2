import { api } from '../api/kanban_api.js';
import { createBoardCard } from '../components/boardCard.js';

export async function renderDashboard(container) {
    container.innerHTML = `
        <div class="page-container">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h1><i data-lucide="layout-dashboard"></i> Your Workspaces</h1>
                <button class="btn"><i data-lucide="plus"></i> New Board</button>
            </div>
            <p style="color: var(--text-muted); margin-top: 2rem;">Loading boards...</p>
        </div>
    `;
    if (window.lucide) window.lucide.createIcons();

    try {
        const boards = await api.getBoards();
        
        let boardsHtml = '<div class="dashboard-grid">';
        if (boards.length === 0) {
            boardsHtml = '<p style="color: var(--text-muted); margin-top: 2rem;">No boards found. Create one to get started!</p>';
        } else {
            boards.forEach(board => {
                boardsHtml += createBoardCard(board);
            });
            boardsHtml += '</div>';
        }

        // 4. Final Render
        container.innerHTML = `
            <div class="page-container">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h1><i data-lucide="layout-dashboard" style="color: var(--accent)"></i> Your Workspaces</h1>
                    <button class="btn" id="new-board-btn"><i data-lucide="plus"></i> New Board</button>
                </div>
                ${boardsHtml}
            </div>
        `;
        if (window.lucide) window.lucide.createIcons();

    } catch (error) {
        container.innerHTML = `
            <div class="page-container">
                <h1 style="color: var(--danger);">Connection Error</h1>
                <p style="color: var(--text-muted); margin-top: 1rem;">Could not connect to the Kanban API. Is your Flask server running?</p>
                <p style="color: var(--danger); font-family: monospace; margin-top: 1rem;">${error.message}</p>
            </div>
        `;
    }
}