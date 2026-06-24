// 1. Import Global Styles
import './assets/variables.css';
import './assets/base.css';
import './assets/layout.css';
import './assets/components.css';

// 2. Import Page Controllers
import { renderDashboard } from './pages/dashboard.js';
import { renderBoard } from './pages/board.js';
import { renderAuth } from './pages/auth.js';
import { api } from './api/kanban_api.js';

const app = document.getElementById('app');

function renderNavHeader(user) {
    const nav = document.createElement('header');
    nav.className = 'global-nav';
    nav.innerHTML = `
        <a href="#dashboard" class="global-nav-brand">
            <i data-lucide="kanban"></i>
            <span>Kanban Space</span>
        </a>
        <div class="global-nav-user-area">
            <span class="global-nav-username">Hello, <strong>${user.username}</strong></span>
            <button class="btn btn-danger" id="logout-btn" style="padding: 0.35rem 0.75rem; font-size: 0.825rem;">
                <i data-lucide="log-out" style="width: 14px; height: 14px;"></i> Log Out
            </button>
        </div>
    `;
    nav.querySelector('#logout-btn').addEventListener('click', async () => {
        await api.logout();
    });
    return nav;
}

function router() {
    const hash = window.location.hash;
    const isAuthenticated = api.isAuthenticated();

    // 1. Auth Route Guard: if not authenticated, redirect to #login
    if (!isAuthenticated) {
        if (hash !== '#login') {
            window.location.hash = '#login';
            return;
        }
        app.innerHTML = '';
        renderAuth(app);
        return;
    }

    // 2. Authenticated user guard: if they try to access #login but are already authenticated, send to #dashboard
    if (hash === '#login') {
        window.location.hash = '#dashboard';
        return;
    }

    // Clear the screen
    app.innerHTML = '';

    // Create a container wrapper for the page content
    const pageContent = document.createElement('div');
    pageContent.className = 'page-content-wrapper';

    // Append the global header navigation
    const user = api.getCurrentUser() || { username: 'Guest' };
    const navHeader = renderNavHeader(user);
    app.appendChild(navHeader);
    app.appendChild(pageContent);

    // Route logic inside the content wrapper
    if (!hash || hash === '#' || hash === '#dashboard') {
        renderDashboard(pageContent);
    } else if (hash.startsWith('#board/')) {
        const boardId = hash.split('/')[1];
        renderBoard(pageContent, boardId);
    } else {
        pageContent.innerHTML = '<h1 style="padding: 2rem; color: var(--danger);">404 - Page Not Found</h1>';
    }

    // Re-initialize Lucide icons every time the DOM changes
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// 3. Listen for URL changes and initial page load
window.addEventListener('hashchange', router);
window.addEventListener('DOMContentLoaded', router);