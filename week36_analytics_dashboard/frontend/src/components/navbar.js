import { toggleTheme } from "../utils/theme.js";

export function renderNavbar(isOnline = true) {
    const container = document.getElementById("navbar-container");
    if (!container) return;

    container.innerHTML = `
        <header class="nav-header">
            <div class="brand-group">
                <span class="brand-icon">📊</span>
                <div>
                    <h1 class="brand-title">PulseMetrics</h1>
                    <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Real-Time Business Intelligence & Telemetry</span>
                </div>
            </div>

            <div style="display: flex; align-items: center; gap: 1rem;">
                <div class="status-beacon ${isOnline ? 'beacon-online' : 'beacon-offline'}">
                    <span>${isOnline ? '●' : '○'}</span>
                    <span>${isOnline ? 'Telemetry Live' : 'Connecting...'}</span>
                </div>

                <button id="theme-toggle-btn" class="btn-outline">
                    ☀️ Light Mode
                </button>
            </div>
        </header>
    `;

    document.getElementById("theme-toggle-btn")?.addEventListener("click", toggleTheme);
}
