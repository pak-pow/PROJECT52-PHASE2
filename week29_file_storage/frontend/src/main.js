/* ═══════════════════════════════════════════════════════════════
   FileVault — Main Application Bootstrapper
   ═══════════════════════════════════════════════════════════════ */

import { login, register, logout } from "./api/fileApi.js";
import { renderDashboard } from "./pages/dashboard.js";
import { renderUpload } from "./pages/upload.js";
import { initPreviewModal } from "./components/preview.js";

// ── State ────────────────────────────────────────────────────
let currentView = "dashboard";
let currentCategory = "all";


// ── Boot ─────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    initPreviewModal();
    setupAuth();
    setupNavigation();

    // Check if user is already logged in
    const token = localStorage.getItem("fv_token");
    if (token) {
        showApp();
    } else {
        showAuth();
    }
});


// ── Auth Screen ──────────────────────────────────────────────
function setupAuth() {
    const form = document.getElementById("auth-form");
    const loginBtn = document.getElementById("auth-login-btn");
    const registerBtn = document.getElementById("auth-register-btn");
    const errorEl = document.getElementById("auth-error");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        await handleAuth("login", errorEl);
    });

    registerBtn.addEventListener("click", async () => {
        await handleAuth("register", errorEl);
    });
}

async function handleAuth(action, errorEl) {
    const username = document.getElementById("auth-username").value.trim();
    const password = document.getElementById("auth-password").value;
    errorEl.textContent = "";

    if (!username || !password) {
        errorEl.textContent = "Please fill in all fields.";
        return;
    }

    try {
        const result = action === "login"
            ? await login(username, password)
            : await register(username, password);

        if (result.ok) {
            localStorage.setItem("fv_token", result.data.token);
            localStorage.setItem("fv_user", result.data.username);
            showApp();
        } else {
            errorEl.textContent = result.data.error || "Something went wrong.";
        }
    } catch {
        errorEl.textContent = "Cannot connect to server.";
    }
}


// ── Navigation ───────────────────────────────────────────────
function setupNavigation() {
    // View tabs
    document.querySelectorAll(".tab-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const view = btn.dataset.view;
            if (view === currentView) return;
            setActiveTab(btn);
            currentView = view;
            renderCurrentView();
        });
    });

    // Category filters
    document.querySelectorAll(".filter-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const cat = btn.dataset.category;
            if (cat === currentCategory && currentView === "dashboard") return;
            setActiveFilter(btn);
            currentCategory = cat;
            // Switch to dashboard if on upload tab
            if (currentView !== "dashboard") {
                currentView = "dashboard";
                setActiveTab(document.querySelector('.tab-btn[data-view="dashboard"]'));
            }
            renderCurrentView();
        });
    });

    // Logout
    document.getElementById("logout-btn").addEventListener("click", async () => {
        await logout();
        showAuth();
    });
}


// ── View Rendering ───────────────────────────────────────────
function renderCurrentView() {
    const main = document.getElementById("main-content");
    const filtersEl = document.getElementById("category-filters");

    if (currentView === "dashboard") {
        filtersEl.style.display = "flex";
        renderDashboard(main, currentCategory);
    } else if (currentView === "upload") {
        filtersEl.style.display = "none";
        renderUpload(main, () => {
            // After upload, switch to dashboard
            currentView = "dashboard";
            setActiveTab(document.querySelector('.tab-btn[data-view="dashboard"]'));
            filtersEl.style.display = "flex";
            renderDashboard(main, currentCategory);
        });
    }
}


// ── Screen Switching ─────────────────────────────────────────
function showAuth() {
    document.getElementById("auth-screen").classList.add("active");
    document.getElementById("app-screen").classList.remove("active");
    document.getElementById("auth-username").value = "";
    document.getElementById("auth-password").value = "";
    document.getElementById("auth-error").textContent = "";
}

function showApp() {
    document.getElementById("auth-screen").classList.remove("active");
    document.getElementById("app-screen").classList.add("active");
    document.getElementById("current-user").textContent = localStorage.getItem("fv_user") || "";
    currentView = "dashboard";
    currentCategory = "all";
    renderCurrentView();
}


// ── Helpers ──────────────────────────────────────────────────
function setActiveTab(activeBtn) {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    activeBtn.classList.add("active");
}

function setActiveFilter(activeBtn) {
    document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
    activeBtn.classList.add("active");
}
