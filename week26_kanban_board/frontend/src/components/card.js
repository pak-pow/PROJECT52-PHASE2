import { escapeHtml } from '../utils/dom.js';

export function createCardHTML(card) {
    const hasDesc = card.description && card.description.trim().length > 0;
    
    return `
        <div class="kanban-card" 
             draggable="true" 
             data-card-id="${card.id}" 
             data-column-id="${card.column_id}"
             data-position="${card.position}">
            
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem;">
                <div class="card-title">${escapeHtml(card.title)}</div>
                
                <div style="display: flex; gap: 2px;">
                    <button class="edit-card-btn" 
                            data-id="${card.id}" 
                            title="Edit Card"
                            style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 2px; border-radius: 4px; display: inline-flex; align-items: center; justify-content: center; transition: color var(--transition-fast);">
                        <i data-lucide="edit-3" style="width: 13px; height: 13px;"></i>
                    </button>
                    <button class="delete-card-btn" 
                            data-id="${card.id}" 
                            data-title="${escapeHtml(card.title)}"
                            title="Delete Card"
                            style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 2px; border-radius: 4px; display: inline-flex; align-items: center; justify-content: center; transition: color var(--transition-fast);">
                        <i data-lucide="trash-2" style="width: 13px; height: 13px;"></i>
                    </button>
                </div>
            </div>
            
            ${hasDesc ? `<div class="card-desc">${escapeHtml(card.description)}</div>` : ''}
        </div>
    `;
}
