import { isLoggedIn, getCurrentUser } from "../utils/authCheck.js";
import { apiLogout } from "../api/authApi.js";
import { toggleTheme } from "../utils/theme.js";
import { escapeHtml } from "../utils/helpers.js";

export function renderNavbar() {
    const header = document.getElementById("app-header");
    if (!header) return;

    const user = getCurrentUser();
    const loggedIn = isLoggedIn();

    header.innerHTML = `
        <div class="header-container">
            <a href="index.html" class="brand-logo">
                <div class="brand-icon">📅</div>
                <span>Bookify</span>
            </a>

            <nav class="nav-links">
                <a href="index.html" class="nav-item ${window.location.pathname.endsWith("index.html") || window.location.pathname.endsWith("/") ? "active" : ""}">Services</a>
                ${loggedIn ? `
                    <a href="dashboard.html" class="nav-item ${window.location.pathname.endsWith("dashboard.html") ? "active" : ""}">My Appointments</a>
                    <span class="user-greeting" style="font-size: 0.9rem; color: var(--text-secondary); font-weight: 500;">
                        👋 ${escapeHtml(user?.display_name || user?.username || "Client")}
                    </span>
                    <button id="btn-logout" class="nav-item" style="background: none; border: none; cursor: pointer;">Logout</button>
                ` : `
                    <a href="login.html" class="nav-item ${window.location.pathname.endsWith("login.html") ? "active" : ""}">Login</a>
                    <a href="register.html" class="btn-primary" style="padding: 0.4rem 1rem; font-size: 0.85rem;">Sign Up</a>
                `}
                <button id="theme-toggle" class="nav-item" aria-label="Toggle Theme" style="background: none; border: none; cursor: pointer; font-size: 1.1rem;">
                    ${document.documentElement.getAttribute("data-theme") === "light" ? "🌙" : "☀️"}
                </button>
            </nav>
        </div>
    `;

    // Attach Logout Event
    const logoutBtn = document.getElementById("btn-logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", async () => {
            await apiLogout();
            window.location.href = "login.html";
        });
    }

    // Attach Theme Toggle Event
    const themeBtn = document.getElementById("theme-toggle");
    if (themeBtn) {
        themeBtn.addEventListener("click", () => {
            const next = toggleTheme();
            themeBtn.textContent = next === "light" ? "🌙" : "☀️";
        });
    }
}
