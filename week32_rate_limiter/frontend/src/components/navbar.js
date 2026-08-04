import { toggleTheme } from "../utils/theme.js";

export function renderNavbar(activePage = "dashboard") {
    const navbarContainer = document.getElementById("navbar-container");
    if (!navbarContainer) return;

    navbarContainer.innerHTML = `
        <header class="app-header">
            <div class="header-container">
                <a href="index.html" class="brand-logo">
                    <div class="brand-icon">🛡️</div>
                    <span>RateLimiter<span style="color: var(--accent-light);">Engine</span></span>
                </a>
                <div class="nav-links">
                    <a href="index.html" class="nav-item ${activePage === 'dashboard' ? 'active' : ''}">⚡ Control Center</a>
                    <a href="login.html" class="nav-item ${activePage === 'login' ? 'active' : ''}">🔑 Login / API Keys</a>
                    <button id="theme-toggle-btn" class="btn-secondary" style="padding: 0.4rem 0.85rem; font-size: 0.9rem;">
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
