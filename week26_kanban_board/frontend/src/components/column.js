import { escapeHtml } from '../utils/dom.js';

export function createColumnHTML(column, cardsHTML = '') {
    return `
        <div class="kanban-column" data-column-id="${column.id}" data-position="${column.position}" draggable="true" data-drag-enabled="false">
            
            <div class="column-header"
                 onmousedown="this.parentElement.dataset.dragEnabled='true'"
                 onmouseup="this.parentElement.dataset.dragEnabled='false'"
                 onmouseleave="this.parentElement.dataset.dragEnabled='false'">
                 
                <input type="text" 
                       class="column-title-input" 
                       value="${escapeHtml(column.title)}" 
                       data-id="${column.id}"
                       data-original-val="${escapeHtml(column.title)}"
                       title="Double click to edit column name"
                       maxlength="100">
                
                <button class="delete-column-btn btn-icon" 
                        data-id="${column.id}" 
                        data-title="${escapeHtml(column.title)}" 
                        title="Delete Column"
                        style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 4px; border-radius: 4px; display: inline-flex; align-items: center; justify-content: center; transition: color var(--transition-fast);">
                    <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
                </button>
            </div>
            
            <div class="cards-container" data-column-id="${column.id}">
                ${cardsHTML}
            </div>
            
            <div style="padding: 0.75rem; border-top: 1px solid rgba(255,255,255,0.03);">
                <button class="btn add-card-btn" 
                        data-column-id="${column.id}" 
                        style="width: 100%; justify-content: center; background-color: transparent; border: 1px dashed var(--border-color); color: var(--text-muted);">
                    <i data-lucide="plus" style="width: 16px; height: 16px;"></i> Add Card
                </button>
            </div>
        </div>
    `;
}