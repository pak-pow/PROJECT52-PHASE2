/**
 * Initializes HTML5 Drag and Drop for Kanban Cards and Columns.
 * @param {Object} callbacks
 * @param {Function} callbacks.onCardMove - Called when a card is dropped: (cardId, targetColumnId, targetPosition)
 * @param {Function} callbacks.onColumnReorder - Called when a column is dragged (optional)
 */

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.kanban-card:not(.dragging)')];

    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;

        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

function getDragAfterColumn(container, x) {
    const draggableElements = [...container.querySelectorAll('.kanban-column:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = x - box.left - box.width / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

function getDragAfterGridElement(container, x, y) {
    const draggableElements = [...container.querySelectorAll('.board-card:not(.dragging)')];
    
    const closest = draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const centerX = box.left + box.width / 2;
        const centerY = box.top + box.height / 2;
        
        const distance = Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2);
        
        if (distance < closest.distance) {
            return { distance: distance, element: child, box: box };
        } else {
            return closest;
        }
    }, { distance: Number.POSITIVE_INFINITY, element: null });

    if (!closest.element) return null;
    
    const box = closest.box;
    const centerX = box.left + box.width / 2;
    const centerY = box.top + box.height / 2;
    
    const isPast = (x > centerX && y >= box.top && y <= box.bottom) || (y > centerY);
    if (isPast) {
        return closest.element.nextElementSibling;
    }
    return closest.element;
}

export function initDragAndDrop(container, onCardMove, onColumnMove, onBoardMove) {
    let draggedElement = null;
    let dragType = null;
    let sourceContainer = null;
    let originalNextSibling = null;

    container.addEventListener('dragstart', (e) => {
        if (e.target.classList.contains('kanban-card')) {
            dragType = 'card';
            draggedElement = e.target;
            sourceContainer = draggedElement.parentElement;
            originalNextSibling = draggedElement.nextElementSibling;
            
            // Timeout ensures the ghost looks normal, but the original turns translucent
            setTimeout(() => draggedElement.classList.add('dragging'), 0);
            
        } else if (e.target.classList.contains('kanban-column')) {
            // SECURITY: Only allow column dragging if the user grabbed the header!
            if (e.target.dataset.dragEnabled !== 'true') {
                e.preventDefault();
                return;
            }
            dragType = 'column';
            draggedElement = e.target;
            sourceContainer = container; 
            originalNextSibling = draggedElement.nextElementSibling;

            setTimeout(() => draggedElement.classList.add('dragging'), 0);
        } else if (e.target.classList.contains('board-card')) {
            // Only allow board dragging if user grabbed the drag handle!
            if (e.target.dataset.dragEnabled !== 'true') {
                e.preventDefault();
                return;
            }
            dragType = 'board';
            draggedElement = e.target;
            sourceContainer = draggedElement.parentElement;
            originalNextSibling = draggedElement.nextElementSibling;

            setTimeout(() => draggedElement.classList.add('dragging'), 0);
        }
    });

    container.addEventListener('dragover', (e) => {
        e.preventDefault(); // Required to allow dropping
        if (!draggedElement) return;

        if (dragType === 'card') {
            // MATCHES YOUR CUSTOM HTML: .cards-container
            const dropZone = e.target.closest('.cards-container');
            if (!dropZone) return;
            
            const afterElement = getDragAfterElement(dropZone, e.clientY);
            if (afterElement == null) {
                dropZone.appendChild(draggedElement);
            } else {
                dropZone.insertBefore(draggedElement, afterElement);
            }
            
        } else if (dragType === 'column') {
            const dropZone = container; 
            const afterElement = getDragAfterColumn(dropZone, e.clientX);
            if (afterElement == null) {
                dropZone.appendChild(draggedElement);
            } else {
                dropZone.insertBefore(draggedElement, afterElement);
            }
        } else if (dragType === 'board') {
            const dropZone = container.querySelector('.dashboard-grid') || container;
            const afterElement = getDragAfterGridElement(dropZone, e.clientX, e.clientY);
            if (afterElement == null) {
                dropZone.appendChild(draggedElement);
            } else {
                dropZone.insertBefore(draggedElement, afterElement);
            }
        }
    });

    container.addEventListener('dragend', (e) => {
        if (!draggedElement) return;
        
        draggedElement.classList.remove('dragging');
        if (dragType === 'column' || dragType === 'board') {
            draggedElement.dataset.dragEnabled = 'false'; // Reset lock
        }
        
        // Cache variables for the rollback function
        const type = dragType;
        const element = draggedElement;
        const originalCol = sourceContainer;
        const originalSib = originalNextSibling;

        // Reset memory
        draggedElement = null;
        dragType = null;
        sourceContainer = null;
        originalNextSibling = null;

        if (type === 'card' && onCardMove) {
            // MATCHES YOUR CUSTOM HTML: dataset.columnId and dataset.cardId
            const newColumnId = element.closest('.kanban-column').dataset.columnId;
            const newPosition = Array.from(element.parentElement.children).indexOf(element);
            const cardId = element.dataset.cardId || element.dataset.id; // Fallback support
            
            onCardMove({
                cardId: cardId,
                newColumnId: newColumnId,
                newPosition: newPosition,
                revert: () => originalCol.insertBefore(element, originalSib)
            });
            
        } else if (type === 'column' && onColumnMove) {
            const newPosition = Array.from(container.querySelectorAll('.kanban-column')).indexOf(element);
            const columnId = element.dataset.columnId || element.dataset.id; // Fallback support
            
            onColumnMove({
                columnId: columnId,
                newPosition: newPosition,
                revert: () => container.insertBefore(element, originalSib)
            });
        } else if (type === 'board' && onBoardMove) {
            const parent = element.parentElement;
            const newPosition = Array.from(parent.children).indexOf(element);
            const boardId = element.dataset.boardId || element.dataset.id;
            
            onBoardMove({
                boardId: boardId,
                newPosition: newPosition,
                revert: () => originalCol.insertBefore(element, originalSib)
            });
        }
    });
}