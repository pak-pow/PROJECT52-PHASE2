import { escapeHtml } from '../utils/dom.js';

export function createCardHTML(card) {
    const hasDesc = card.description && card.description.trim().length > 0;
    
    return `
        <div class="kanban-card" 
             draggable="true" 
             data-card-id="${card.id}" 
             data-column-id="${card.column_id}"
             data-position="${card.position}">
            
            <div class="kanban-card-header">
                <div class="card-title">${escapeHtml(card.title)}</div>
                
                <div class="kanban-card-actions">
                    <button class="edit-card-btn" 
                            data-id="${card.id}" 
                            title="Edit Card">
                        <i data-lucide="edit-3" style="width: 13px; height: 13px;"></i>
                    </button>
                    <button class="delete-card-btn" 
                            data-id="${card.id}" 
                            data-title="${escapeHtml(card.title)}"
                            title="Delete Card">
                        <i data-lucide="trash-2" style="width: 13px; height: 13px;"></i>
                    </button>
                </div>
            </div>
            
            ${hasDesc ? `<div class="card-desc">${escapeHtml(card.description)}</div>` : ''}
        </div>
    `;
}
