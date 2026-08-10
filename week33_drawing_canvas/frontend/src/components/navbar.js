import { toggleTheme } from "../utils/theme.js";

export function renderNavbar(roomCode = null) {
    const navbarContainer = document.getElementById("navbar-container");
    if (!navbarContainer) return;

    const roomBadgeHtml = roomCode ? `
        <div class="room-badge">
            <span>Room Code:</span>
            <strong style="color: var(--accent-light); font-family: monospace;">${roomCode}</strong>
        </div>
    ` : '';

    navbarContainer.innerHTML = `
        <header class="app-header">
            <div class="header-container">
                <a href="index.html" class="brand-logo">
                    <div class="brand-icon">🎨</div>
                    <span>Canvas<span style="color: var(--accent-light);">Sync</span></span>
                </a>
                
                ${roomBadgeHtml}

                <div class="header-actions">
                    <button id="theme-toggle-btn" class="btn-secondary" style="padding: 0.4rem 0.85rem; font-size: 0.85rem;">
                        🌙 Toggle Theme
                    </button>
                </div>
            </div>
        </header>
    `;

    document.getElementById("theme-toggle-btn")?.addEventListener("click", () => {
        const newTheme = toggleTheme();
        const btn = document.getElementById("theme-toggle-btn");
        if (btn) btn.textContent = newTheme === "dark" ? "🌙 Toggle Theme" : "☀️ Toggle Theme";
    });
}
