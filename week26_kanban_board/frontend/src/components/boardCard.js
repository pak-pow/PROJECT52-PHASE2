import { escapeHtml } from '../utils/dom.js';

export function createBoardCard(board) {
    const date = new Date(board.created_at).toLocaleDateString();
    
    return `
        <a href="#board/${board.id}" class="board-card" data-board-id="${board.id}" data-position="${board.position}" draggable="true" data-drag-enabled="false" style="border-top: 4px solid ${escapeHtml(board.accent_color)}; --local-accent: ${escapeHtml(board.accent_color)};">
            <div class="board-card-header">
                <h3 class="board-card-title">
                    ${escapeHtml(board.title)}
                </h3>
                <div class="board-card-actions">
                    <div class="board-drag-handle" 
                         title="Drag to reorder"
                         onmousedown="this.closest('.board-card').dataset.dragEnabled='true'"
                         onmouseup="this.closest('.board-card').dataset.dragEnabled='false'"
                         onmouseleave="this.closest('.board-card').dataset.dragEnabled='false'"
                         onclick="event.preventDefault(); event.stopPropagation();">
                        <i data-lucide="grip-vertical" style="width: 16px; height: 16px;"></i>
                    </div>
                    <button class="edit-board-btn" 
                            data-id="${board.id}" 
                            title="Edit Board">
                        <i data-lucide="edit-3" style="width: 16px; height: 16px;"></i>
                    </button>
                    <button class="delete-board-btn" 
                            data-id="${board.id}" 
                            data-title="${escapeHtml(board.title)}" 
                            title="Delete Board">
                        <i data-lucide="trash-2" style="width: 16px; height: 16px;"></i>
                    </button>
                </div>
            </div>
            
            <p class="board-card-desc">
                ${escapeHtml(board.description || 'No description provided.')}
            </p>
            
            <div class="board-card-footer">
                <span class="board-card-date">
                    <i data-lucide="calendar" style="width: 14px; height: 14px;"></i> ${date}
                </span>
            </div>
        </a>
    `;
}