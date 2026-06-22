/**
 * Initializes HTML5 Drag and Drop for Kanban Cards and Columns.
 * @param {Object} callbacks
 * @param {Function} callbacks.onCardMove - Called when a card is dropped: (cardId, targetColumnId, targetPosition)
 * @param {Function} callbacks.onColumnReorder - Called when a column is dragged (optional)
 */
export function initDragAndDrop({ onCardMove }) {
    let draggedCard = null;

    // Attach to document to handle dynamically rendered cards/columns
    document.addEventListener('dragstart', (e) => {
        const card = e.target.closest('.kanban-card');
        if (card) {
            draggedCard = card;
            card.classList.add('dragging');
            
            // Set drag data
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', card.getAttribute('data-card-id'));
        }
    });

    document.addEventListener('dragend', (e) => {
        const card = e.target.closest('.kanban-card');
        if (card) {
            card.classList.remove('dragging');
        }
        
        // Remove drag highlights from all containers
        document.querySelectorAll('.cards-container').forEach(container => {
            container.classList.remove('drag-over');
        });
        
        draggedCard = null;
    });

    document.addEventListener('dragover', (e) => {
        const container = e.target.closest('.cards-container');
        if (!container || !draggedCard) return;

        e.preventDefault(); // Required to allow dropping
        
        container.classList.add('drag-over');

        // Visual feedback: find closest card below cursor and append/insert before it
        const afterElement = getDragAfterElement(container, e.clientY);
        if (afterElement == null) {
            container.appendChild(draggedCard);
        } else {
            container.insertBefore(draggedCard, afterElement);
        }
    });

    document.addEventListener('dragleave', (e) => {
        const container = e.target.closest('.cards-container');
        if (container) {
            // Check if cursor actually left the container, not just moved over a card
            const rect = container.getBoundingClientRect();
            if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) {
                container.classList.remove('drag-over');
            }
        }
    });

    document.addEventListener('drop', async (e) => {
        const container = e.target.closest('.cards-container');
        if (!container || !draggedCard) return;

        e.preventDefault();
        container.classList.remove('drag-over');

        const cardId = parseInt(draggedCard.getAttribute('data-card-id'), 10);
        const targetColumnId = parseInt(container.getAttribute('data-column-id'), 10);

        // Find position index of draggedCard inside this container
        const cardsInContainer = Array.from(container.querySelectorAll('.kanban-card'));
        const newPosition = cardsInContainer.indexOf(draggedCard);

        if (cardId && targetColumnId !== undefined && newPosition !== -1) {
            onCardMove(cardId, targetColumnId, newPosition);
        }
    });
}

/**
 * Calculates which card element the cursor is dragging over.
 * Returns the card element immediately below the cursor.
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

export function initDragAndDrop(container, onCardMove, onColumnMove) {
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
            setTimeout(() => draggedElement.classList.add('dragging'), 0);
            
        } else if (e.target.classList.contains('kanban-column')) {
            if (e.target.dataset.dragEnabled !== 'true') {
                e.preventDefault();
                return;
            }

            dragType = 'column';
            draggedElement = e.target;
            sourceContainer = container; 
            originalNextSibling = draggedElement.nextElementSibling;

            setTimeout(() => draggedElement.classList.add('dragging'), 0);
        }
    });

    container.addEventListener('dragover', (e) => {
        e.preventDefault(); 
        if (!draggedElement) return;

        if (dragType === 'card') {
            
            const dropZone = e.target.closest('.column-cards');
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
        }
    });

    container.addEventListener('dragend', (e) => {
        
        if (!draggedElement) return;
        
        draggedElement.classList.remove('dragging');
        if (dragType === 'column') {
            draggedElement.dataset.dragEnabled = 'false'; // Reset lock
        }
        
        const type = dragType;
        const element = draggedElement;
        const originalCol = sourceContainer;
        const originalSib = originalNextSibling;

        draggedElement = null;
        dragType = null;
        sourceContainer = null;
        originalNextSibling = null;

        if (type === 'card' && onCardMove) {
            const newColumnId = element.closest('.kanban-column').dataset.id;
            const newPosition = Array.from(element.parentElement.children).indexOf(element);
            
            onCardMove({
                cardId: element.dataset.id,
                newColumnId: newColumnId,
                newPosition: newPosition,
                revert: () => originalCol.insertBefore(element, originalSib)
            });
            
        } else if (type === 'column' && onColumnMove) {
            const newPosition = Array.from(container.querySelectorAll('.kanban-column')).indexOf(element);
            
            onColumnMove({
                columnId: element.dataset.id,
                newPosition: newPosition,
                revert: () => container.insertBefore(element, originalSib)
            });
        }
    });
}