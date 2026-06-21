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
