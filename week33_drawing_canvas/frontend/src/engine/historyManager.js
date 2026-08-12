export class HistoryManager {
    /**
     * In-Memory Canvas State History Manager for Undo/Redo.
     */
    constructor(maxHistory = 30) {
        this.maxHistory = maxHistory;
        this.undoStack = [];
        this.redoStack = [];
    }

    saveState(canvasContext, canvasElement) {
        const dpr = window.devicePixelRatio || 1;
        const width = canvasElement.width / dpr;
        const height = canvasElement.height / dpr;

        try {
            const imageData = canvasContext.getImageData(0, 0, width, height);
            this.undoStack.push(imageData);
            if (this.undoStack.length > this.maxHistory) {
                this.undoStack.shift();
            }
            // Clear redo stack on new action
            this.redoStack = [];
        } catch (e) {
            console.warn("Could not capture canvas state:", e);
        }
    }

    undo(canvasContext, canvasElement) {
        if (this.undoStack.length <= 1) return false;

        // Move current state to redo stack
        const current = this.undoStack.pop();
        this.redoStack.push(current);

        // Restore previous state
        const previous = this.undoStack[this.undoStack.length - 1];
        if (previous) {
            canvasContext.putImageData(previous, 0, 0);
            return true;
        }
        return false;
    }

    redo(canvasContext, canvasElement) {
        if (this.redoStack.length === 0) return false;

        const next = this.redoStack.pop();
        this.undoStack.push(next);
        canvasContext.putImageData(next, 0, 0);
        return true;
    }

    canUndo() {
        return this.undoStack.length > 1;
    }

    canRedo() {
        return this.redoStack.length > 0;
    }

    clear() {
        this.undoStack = [];
        this.redoStack = [];
    }
}
