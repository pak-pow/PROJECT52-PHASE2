/**
 * sidebar.js — Shared sidebar component for multi-page layout.
 */
import { clearSession, apiLogout } from "../api/authApi.js";
import { avatarUrl } from "../api/userApi.js";
import { getCurrentUser } from "../utils/state.js";
import { initTheme, toggleTheme } from "../utils/theme.js";
import { escapeHtml } from "../utils/helpers.js";

export function initSidebar(activePageName) {
    initTheme();
    const currentUser = getCurrentUser();
    if (!currentUser) return;

    // Active navigation state
    document.querySelectorAll(".nav-item").forEach(el => {
        const page = el.dataset.page;
        const isActive = page === activePageName;
        el.classList.toggle("active", isActive);
        // Ensure profile link leads to current user's profile page if no u param
        if (page === "profile") {
            el.href = `profile.html?u=${encodeURIComponent(currentUser.username)}`;
        }
    });

    // Populate user info
    const sidebarDisplayName = document.getElementById("sidebar-display-name");
    const sidebarUsername    = document.getElementById("sidebar-username");
    const sidebarAvatar      = document.getElementById("sidebar-avatar");

    if (sidebarDisplayName) sidebarDisplayName.textContent = currentUser.displayName || currentUser.username;
    if (sidebarUsername)    sidebarUsername.textContent    = `@${currentUser.username}`;
    if (sidebarAvatar) {
        const initial = (currentUser.displayName || currentUser.username || "?")[0].toUpperCase();
        const src = avatarUrl(currentUser.username);
        sidebarAvatar.innerHTML = `
            <span class="avatar-initial">${escapeHtml(initial)}</span>
            <img class="avatar-img" src="${src}" alt="" loading="eager" onerror="this.remove()" />
        `;
    }

    // Logout button
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", async () => {
            await apiLogout();
            clearSession();
            window.location.href = "login.html";
        });
    }

    // Theme toggle button
    const themeBtn = document.getElementById("theme-toggle-btn");
    if (themeBtn) {
        themeBtn.addEventListener("click", () => {
            const nextTheme = toggleTheme();
            themeBtn.textContent = nextTheme === "dark" ? "🌙" : "☀️";
        });
    }

    // Sidebar compose button
    const sidebarComposeBtn = document.getElementById("sidebar-compose-btn");
    const composeInput = document.getElementById("compose-input");
    if (sidebarComposeBtn) {
        sidebarComposeBtn.addEventListener("click", () => {
            if (window.location.pathname.endsWith("feed.html")) {
                if (composeInput) composeInput.focus();
            } else {
                window.location.href = "feed.html";
            }
        });
    }

    // Inject Mobile Bottom Navigation Bar if not present
    if (!document.querySelector(".mobile-nav")) {
        const mobileNav = document.createElement("nav");
        mobileNav.className = "mobile-nav";
        mobileNav.setAttribute("aria-label", "Mobile navigation");
        mobileNav.innerHTML = `
            <a href="feed.html" class="mobile-nav-item ${activePageName === "feed" ? "active" : ""}">
                <span class="mobile-nav-icon">🏠</span>
                <span class="mobile-nav-label">Home</span>
            </a>
            <a href="explore.html" class="mobile-nav-item ${activePageName === "explore" ? "active" : ""}">
                <span class="mobile-nav-icon">🔥</span>
                <span class="mobile-nav-label">Explore</span>
            </a>
            <a href="profile.html?u=${encodeURIComponent(currentUser.username)}" class="mobile-nav-item ${activePageName === "profile" ? "active" : ""}">
                <span class="mobile-nav-icon">👤</span>
                <span class="mobile-nav-label">Profile</span>
            </a>
        `;
        document.body.appendChild(mobileNav);
    }
}
