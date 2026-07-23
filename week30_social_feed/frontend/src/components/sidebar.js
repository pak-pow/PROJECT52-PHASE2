/**
 * sidebar.js — Shared sidebar component for multi-page layout.
 */
import { clearSession, apiLogout } from "../api/authApi.js";
import { avatarUrl } from "../api/userApi.js";
import { getCurrentUser } from "../utils/state.js";

export function initSidebar(activePageName) {
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
        sidebarAvatar.textContent = (currentUser.displayName || currentUser.username || "?")[0].toUpperCase();
        const img = new Image();
        img.onload = () => {
            sidebarAvatar.textContent = "";
            sidebarAvatar.style.cssText = `background-image:url(${img.src});background-size:cover;background-position:center;`;
        };
        img.src = avatarUrl(currentUser.username);
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
}
