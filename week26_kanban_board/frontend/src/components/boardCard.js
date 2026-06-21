import { escapeHtml } from '../utils/dom.js';

export function createBoardCard(board) {
    const date = new Date(board.created_at).toLocaleDateString();
    
    return `
        <a href="#board/${board.id}" class="board-card" style="border-top: 4px solid ${escapeHtml(board.accent_color)};">
            <h3 style="margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                ${escapeHtml(board.title)}
            </h3>
            <p style="color: var(--text-muted); font-size: 0.875rem; margin-bottom: 1rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                ${escapeHtml(board.description || 'No description provided.')}
            </p>
            <div style="font-size: 0.75rem; color: var(--text-muted); display: flex; justify-content: space-between;">
                <span style="display: flex; align-items: center; gap: 4px;">
                    <i data-lucide="calendar" style="width: 14px; height: 14px;"></i> ${date}
                </span>
                <span>ID: ${board.id}</span>
            </div>
        </a>
    `;
}