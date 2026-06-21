// 1. Import Global Styles
import './assets/variables.css';
import './assets/base.css';
import './assets/layout.css';
import './assets/components.css';

// 2. Import Page Controllers
import { renderDashboard } from './pages/dashboard.js';
import { renderBoard } from './pages/board.js';

const app = document.getElementById('app');

function router() {
    // Get the current URL hash
    const hash = window.location.hash;

    // Clear the screen
    app.innerHTML = '';

    // Route logic
    if (!hash || hash === '#' || hash === '#dashboard') {
        renderDashboard(app);
    } else if (hash.startsWith('#board/')) {
        const boardId = hash.split('/')[1];
        renderBoard(app, boardId);
    } else {
        app.innerHTML = '<h1 style="padding: 2rem; color: var(--danger);">404 - Page Not Found</h1>';
    }

    // Re-initialize Lucide icons every time the DOM changes
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// 3. Listen for URL changes and initial page load
window.addEventListener('hashchange', router);
window.addEventListener('DOMContentLoaded', router);