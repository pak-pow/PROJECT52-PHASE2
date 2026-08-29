import { toggleTheme } from "../utils/theme.js";

export function renderNavbar(isOnline = true) {
    const container = document.getElementById("navbar-container");
    if (!container) return;

    container.innerHTML = `
        <header class="nav-header">
            <div class="brand-group">
                <span class="brand-icon">🔔</span>
                <div>
                    <h1 class="brand-title">NotificationEngine</h1>
                    <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Multi-Channel Queue & Dispatcher</span>
                </div>
            </div>

            <div style="display: flex; align-items: center; gap: 1rem;">
                <div id="server-status-badge" class="server-status-pill ${isOnline ? 'status-online' : 'status-offline'}">
                    <span>${isOnline ? '●' : '○'}</span>
                    <span id="server-status-text">${isOnline ? 'Server Online' : 'Connecting...'}</span>
                </div>

                <button id="theme-toggle-btn" class="btn-outline" style="padding: 0.4rem 0.8rem; font-size: 0.82rem;">
                    ☀️ Light Mode
                </button>
            </div>
        </header>
    `;

    document.getElementById("theme-toggle-btn")?.addEventListener("click", toggleTheme);
}
