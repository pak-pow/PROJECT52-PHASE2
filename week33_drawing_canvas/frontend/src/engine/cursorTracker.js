import { escapeHtml } from "../utils/helpers.js";

export class CursorTracker {
    /**
     * Renders floating remote peer cursors over the canvas.
     */
    constructor(containerElement) {
        this.container = containerElement;
        this.remoteCursors = {}; // sid -> DOM element
        this.lastMoveEmit = 0;
    }

    updateRemoteCursor(data) {
        const { sid, username, color, x, y } = data;
        if (!sid || x === undefined || y === undefined) return;

        let cursorEl = this.remoteCursors[sid];
        if (!cursorEl) {
            cursorEl = document.createElement("div");
            cursorEl.className = "remote-cursor-badge";
            cursorEl.style.borderColor = color || "#3b82f6";
            cursorEl.innerHTML = `
                <svg class="cursor-pointer-svg" viewBox="0 0 24 24" fill="${color || '#3b82f6'}" width="18" height="18">
                    <path d="M3 3l7 18 3-7 7-3L3 3z"/>
                </svg>
                <span class="cursor-label" style="background-color: ${color || '#3b82f6'};">${escapeHtml(username)}</span>
            `;
            this.container.appendChild(cursorEl);
            this.remoteCursors[sid] = cursorEl;
        }

        // Position cursor badge
        cursorEl.style.transform = `translate3d(${x}px, ${y}px, 0)`;

        // Clear cursor after 5 seconds of inactivity
        clearTimeout(cursorEl._timeout);
        cursorEl._timeout = setTimeout(() => {
            cursorEl.remove();
            delete this.remoteCursors[sid];
        }, 5000);
    }

    removeCursor(sid) {
        if (this.remoteCursors[sid]) {
            this.remoteCursors[sid].remove();
            delete this.remoteCursors[sid];
        }
    }

    clearAll() {
        Object.values(this.remoteCursors).forEach(el => el.remove());
        this.remoteCursors = {};
    }
}
