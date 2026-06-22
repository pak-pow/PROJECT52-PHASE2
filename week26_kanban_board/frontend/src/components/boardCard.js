import { escapeHtml } from '../utils/dom.js';

export function createBoardCard(board) {
    const date = new Date(board.created_at).toLocaleDateString();
    
    return `
        <a href="#board/${board.id}" class="board-card" style="border-top: 4px solid ${escapeHtml(board.accent_color)}; --local-accent: ${escapeHtml(board.accent_color)}; position: relative;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; gap: 1rem;">
                <h3 style="margin: 0; font-size: 1.1rem; line-height: 1.3;">
                    ${escapeHtml(board.title)}
                </h3>
                <div style="display: flex; gap: 4px; align-items: center;">
                    <button class="edit-board-btn" 
                            data-id="${board.id}" 
                            title="Edit Board"
                            style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 4px; border-radius: 4px; display: inline-flex; align-items: center; justify-content: center; transition: color var(--transition-fast);">
                        <i data-lucide="edit-3" style="width: 16px; height: 16px;"></i>
                    </button>
                    <button class="delete-board-btn" 
                            data-id="${board.id}" 
                            data-title="${escapeHtml(board.title)}" 
                            title="Delete Board"
                            style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 4px; border-radius: 4px; display: inline-flex; align-items: center; justify-content: center; transition: color var(--transition-fast), background-color var(--transition-fast);">
                        <i data-lucide="trash-2" style="width: 16px; height: 16px;"></i>
                    </button>
                </div>
            </div>
            
            <p style="color: var(--text-muted); font-size: 0.875rem; margin-bottom: 1.5rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 2.5rem; line-height: 1.4;">
                ${escapeHtml(board.description || 'No description provided.')}
            </p>
            
            <div style="font-size: 0.75rem; color: var(--text-muted); display: flex; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.03); padding-top: 0.75rem;">
                <span style="display: flex; align-items: center; gap: 6px;">
                    <i data-lucide="calendar" style="width: 14px; height: 14px;"></i> ${date}
                </span>
                <span style="opacity: 0.8;">Board ID: ${board.id}</span>
            </div>
        </a>
    `;
}