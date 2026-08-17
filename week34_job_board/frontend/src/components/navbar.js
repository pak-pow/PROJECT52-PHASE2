import { getStoredUser, logoutUser } from "../utils/authCheck.js";
import { toggleTheme } from "../utils/theme.js";

export function renderNavbar(activeNav = "catalog") {
    const container = document.getElementById("navbar-container");
    if (!container) return;

    const user = getStoredUser();
    let authNavHtml = "";

    if (user) {
        if (user.role === "employer") {
            authNavHtml = `
                <a href="employer.html" class="nav-link ${activeNav === 'employer' ? 'active' : ''}">Briefcase Employer Dashboard</a>
                <span class="user-badge">Building ${user.company_name || user.username}</span>
                <button id="logout-btn" class="btn-sm-outline">Logout</button>
            `;
        } else {
            authNavHtml = `
                <a href="dashboard.html" class="nav-link ${activeNav === 'dashboard' ? 'active' : ''}">User Applications & Saved</a>
                <span class="user-badge">User ${user.username}</span>
                <button id="logout-btn" class="btn-sm-outline">Logout</button>
            `;
        }
    } else {
        authNavHtml = `
            <a href="login.html" class="nav-link ${activeNav === 'login' ? 'active' : ''}">Sign In</a>
            <a href="register.html" class="btn-primary-sm">Register</a>
        `;
    }

    container.innerHTML = `
        <nav class="navbar">
            <div class="navbar-left">
                <a href="index.html" class="brand-logo">
                    <span class="logo-icon">💼</span> Tech<span class="logo-accent">Jobs</span>
                </a>
            </div>

            <div class="navbar-right">
                <a href="index.html" class="nav-link ${activeNav === 'catalog' ? 'active' : ''}">Browse Jobs</a>
                ${authNavHtml}
                <button id="theme-toggle-btn" class="theme-btn" title="Toggle Dark/Light Mode">🌙</button>
            </div>
        </nav>
    `;

    document.getElementById("theme-toggle-btn")?.addEventListener("click", () => {
        const next = toggleTheme();
        const btn = document.getElementById("theme-toggle-btn");
        if (btn) btn.textContent = next === "dark" ? "🌙" : "☀️";
    });

    document.getElementById("logout-btn")?.addEventListener("click", () => {
        logoutUser();
    });
}
