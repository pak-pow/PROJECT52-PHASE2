/**
 * admin.js — Admin dashboard controller
 * Handles login/logout, messages tab, and projects tab.
 */

import {
    adminLogin, adminLogout,
    getMessages, toggleRead, deleteMessage,
    getProjects, createProject, updateProject, deleteProject,
} from "./api.js";

// ── Elements ───────────────────────────────────────────────────────────────

const loginWrapper    = document.getElementById("admin-login");
const dashboard       = document.getElementById("admin-dashboard");
const loginForm       = document.getElementById("login-form");
const loginError      = document.getElementById("login-error");
const loginBtn        = document.getElementById("login-btn");
const loginText       = document.getElementById("login-text");
const loginSpinner    = document.getElementById("login-spinner");
const logoutBtn       = document.getElementById("logout-btn");

const tabBtns         = document.querySelectorAll(".tab-btn");
const tabContents     = document.querySelectorAll(".tab-content");

const unreadBadge     = document.getElementById("unread-badge");
const messagesList    = document.getElementById("messages-list");
const messagesLoading = document.getElementById("messages-loading");
const messagesEmpty   = document.getElementById("messages-empty");
const refreshBtn      = document.getElementById("refresh-messages-btn");

const projectsList    = document.getElementById("projects-list");
const projectsLoading = document.getElementById("projects-loading");
const projectsEmpty   = document.getElementById("projects-empty");
const addProjectBtn   = document.getElementById("add-project-btn");
const projectFormWrap = document.getElementById("project-form-wrapper");
const projectForm     = document.getElementById("project-form");
const projectFormTitle= document.getElementById("project-form-title");
const cancelProjectBtn= document.getElementById("cancel-project-btn");
const projectFormError= document.getElementById("project-form-error");
const adminToast      = document.getElementById("admin-toast");

const statUnreadCount   = document.getElementById("stat-unread-count");
const statProjectsCount = document.getElementById("stat-projects-count");
const statCompletedCount = document.getElementById("stat-completed-count");

const confirmModal      = document.getElementById("confirm-modal");
const confirmTitle      = document.getElementById("confirm-title");
const confirmMessage    = document.getElementById("confirm-message");
const confirmBtnCancel  = document.getElementById("confirm-btn-cancel");
const confirmBtnOk      = document.getElementById("confirm-btn-ok");

let loadedMessages = [];
let loadedProjects = [];

// NEW: Message filtering state and DOM references
const msgSearchInput   = document.getElementById("msg-search-input");
const msgFilterPills   = document.getElementById("msg-filter-pills");
let currentMsgSearch   = "";
let currentMsgFilter   = "all";

// ── Init ───────────────────────────────────────────────────────────────────

function init() {
    const token = localStorage.getItem("admin_token");
    if (token) {
        showDashboard();
        loadMessages();
        loadAdminProjects();
    } else {
        showLogin();
    }
}

function showLogin() {
    loginWrapper.classList.remove("hidden");
    dashboard.classList.add("hidden");
}

function showDashboard() {
    loginWrapper.classList.add("hidden");
    dashboard.classList.remove("hidden");
}

// ── Login ──────────────────────────────────────────────────────────────────

loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    loginError.classList.add("hidden");
    loginBtn.disabled = true;
    loginText.textContent = "Verifying...";
    loginSpinner.classList.remove("hidden");

    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value.trim();

    try {
        const token = await adminLogin(username, password);
        localStorage.setItem("admin_token", token);
        showDashboard();
        loadMessages();
        loadAdminProjects();
    } catch (err) {
        loginError.textContent = err.message;
        loginError.classList.remove("hidden");
    } finally {
        loginBtn.disabled = false;
        loginText.textContent = "Login";
        loginSpinner.classList.add("hidden");
    }
});

// ── Logout ─────────────────────────────────────────────────────────────────

logoutBtn.addEventListener("click", async () => {
    await adminLogout();
    showLogin();
    loginForm.reset();
});

// ── Tabs ───────────────────────────────────────────────────────────────────

tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
        tabBtns.forEach((b) => b.classList.remove("tab-active"));
        tabContents.forEach((c) => c.classList.add("hidden"));
        btn.classList.add("tab-active");
        document.getElementById(`tab-${btn.dataset.tab}`).classList.remove("hidden");
    });
});

// ── Messages ───────────────────────────────────────────────────────────────

async function loadMessages() {
    setLoading("messages", true);
    try {
        const messages = await getMessages();
        loadedMessages = messages;
        renderMessages(messages);
        updateStats();
    } catch {
        messagesLoading.textContent = "Failed to load messages. Try refreshing.";
    }
}

function renderMessages(messages) {
    setLoading("messages", false);

    // NEW: Apply local search and read/unread filters
    let filtered = messages;

    if (currentMsgFilter === "unread") {
        filtered = filtered.filter((m) => !m.is_read);
    } else if (currentMsgFilter === "read") {
        filtered = filtered.filter((m) => m.is_read);
    }

    if (currentMsgSearch) {
        filtered = filtered.filter((m) => 
            (m.name || "").toLowerCase().includes(currentMsgSearch) ||
            (m.email || "").toLowerCase().includes(currentMsgSearch) ||
            (m.subject || "").toLowerCase().includes(currentMsgSearch) ||
            (m.message || "").toLowerCase().includes(currentMsgSearch)
        );
    }

    const unread = messages.filter((m) => !m.is_read).length;
    unreadBadge.textContent = unread;
    unreadBadge.classList.toggle("hidden", unread === 0);

    if (!filtered.length) {
        messagesEmpty.classList.remove("hidden");
        if (currentMsgSearch || currentMsgFilter !== "all") {
            messagesEmpty.querySelector("p").textContent = "🔍 No matching messages found.";
        } else {
            messagesEmpty.querySelector("p").textContent = "📭 No messages yet.";
        }
        messagesList.classList.add("hidden");
        return;
    }

    messagesEmpty.classList.add("hidden");
    messagesList.classList.remove("hidden");
    messagesList.innerHTML = filtered.map((m) => `
        <div class="message-card glass-card ${m.is_read ? "msg-read" : "msg-unread"}" data-id="${m.id}">
            <div class="msg-meta">
                <span class="msg-name">${escHtml(m.name)}</span>
                <span class="msg-email">${escHtml(m.email)}</span>
                <span class="msg-date">${formatDate(m.created_at)}</span>
                ${!m.is_read ? '<span class="unread-dot"></span>' : ""}
            </div>
            <p class="msg-subject">${escHtml(m.subject)}</p>
            <p class="msg-body">${escHtml(m.message)}</p>
            <div class="msg-actions">
                <button class="btn btn-outline btn-sm toggle-read-btn" data-id="${m.id}" data-read="${m.is_read}">
                    ${m.is_read ? "Mark Unread" : "Mark Read"}
                </button>
                <button class="btn btn-danger btn-sm delete-msg-btn" data-id="${m.id}">Delete</button>
            </div>
        </div>
    `).join("");

    messagesList.querySelectorAll(".toggle-read-btn").forEach((btn) => {
        btn.addEventListener("click", async () => {
            try {
                await toggleRead(btn.dataset.id);
                loadMessages();
            } catch { showToast("Failed to update message", "error"); }
        });
    });

    messagesList.querySelectorAll(".delete-msg-btn").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const confirmed = await showConfirm("Delete Message", "Are you sure you want to permanently delete this message?");
            if (!confirmed) return;
            try {
                await deleteMessage(btn.dataset.id);
                btn.closest(".message-card").remove();
                showToast("Message deleted");
                loadedMessages = loadedMessages.filter(m => m.id !== parseInt(btn.dataset.id));
                updateStats();
                loadMessages();
            } catch { showToast("Failed to delete", "error"); }
        });
    });
}

refreshBtn.addEventListener("click", loadMessages);

// NEW: Search & filtering listeners for inbox
if (msgSearchInput) {
    msgSearchInput.addEventListener("input", (e) => {
        currentMsgSearch = e.target.value.toLowerCase().trim();
        renderMessages(loadedMessages);
    });
}

if (msgFilterPills) {
    msgFilterPills.addEventListener("click", (e) => {
        const btn = e.target.closest(".filter-btn");
        if (!btn) return;

        msgFilterPills.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");

        currentMsgFilter = btn.dataset.filter;
        renderMessages(loadedMessages);
    });
}

// ── Admin Projects ─────────────────────────────────────────────────────────

async function loadAdminProjects() {
    setLoading("projects", true);
    try {
        const projects = await getProjects();
        loadedProjects = projects;
        renderAdminProjects(projects);
        updateStats();
    } catch {
        projectsLoading.textContent = "Failed to load projects.";
    }
}

function renderAdminProjects(projects) {
    setLoading("projects", false);

    if (!projects.length) {
        projectsEmpty.classList.remove("hidden");
        projectsList.classList.add("hidden");
        return;
    }

    projectsEmpty.classList.add("hidden");
    projectsList.classList.remove("hidden");
    projectsList.innerHTML = projects.map((p) => `
        <div class="project-admin-row glass-card" data-id="${p.id}">
            <div class="proj-info">
                ${p.featured === 1 ? '<span class="admin-featured-star" title="Featured project">★</span>' : ""}
                <span class="proj-title">${escHtml(p.title)}</span>
                <span class="status-badge status-${slugify(p.status)}">${escHtml(p.status)}</span>
                <span class="proj-tech">${escHtml(p.tech_stack)}</span>
            </div>
            <div class="proj-actions">
                <button class="btn btn-outline btn-sm edit-project-btn" data-id="${p.id}">Edit</button>
                <button class="btn btn-danger btn-sm delete-project-btn" data-id="${p.id}">Delete</button>
            </div>
        </div>
    `).join("");

    // Attach edit buttons
    projectsList.querySelectorAll(".edit-project-btn").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const projects = await getProjects();
            const project  = projects.find((p) => p.id === parseInt(btn.dataset.id));
            if (project) openProjectForm(project);
        });
    });

    // Attach delete buttons
    projectsList.querySelectorAll(".delete-project-btn").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const confirmed = await showConfirm("Delete Project", "Are you sure you want to permanently delete this project?");
            if (!confirmed) return;
            try {
                await deleteProject(btn.dataset.id);
                showToast("Project deleted");
                loadedProjects = loadedProjects.filter(p => p.id !== parseInt(btn.dataset.id));
                updateStats();
                loadAdminProjects();
            } catch { showToast("Failed to delete project", "error"); }
        });
    });
}

// ── Project Form ───────────────────────────────────────────────────────────

addProjectBtn.addEventListener("click", () => openProjectForm());

cancelProjectBtn.addEventListener("click", () => {
    projectFormWrap.classList.add("hidden");
    projectForm.reset();
    document.getElementById("proj-featured").checked = false;
});

function openProjectForm(project = null) {
    projectFormTitle.textContent = project ? "Edit Project" : "New Project";
    document.getElementById("project-id").value       = project?.id        || "";
    document.getElementById("proj-title").value       = project?.title      || "";
    document.getElementById("proj-description").value = project?.description || "";
    document.getElementById("proj-tech").value        = project?.tech_stack  || "";
    document.getElementById("proj-github").value      = project?.github_url  || "";
    document.getElementById("proj-live").value        = project?.live_url    || "";
    document.getElementById("proj-status").value      = project?.status      || "In Progress";
    document.getElementById("proj-order").value       = project?.sort_order  ?? 0;
    document.getElementById("proj-featured").checked  = project?.featured === 1;
    projectFormError.classList.add("hidden");
    projectFormWrap.classList.remove("hidden");
    projectFormWrap.scrollIntoView({ behavior: "smooth" });
}

projectForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    projectFormError.classList.add("hidden");

    const id   = document.getElementById("project-id").value;
    const data = {
        title:       document.getElementById("proj-title").value.trim(),
        description: document.getElementById("proj-description").value.trim(),
        tech_stack:  document.getElementById("proj-tech").value.trim(),
        github_url:  document.getElementById("proj-github").value.trim() || null,
        live_url:    document.getElementById("proj-live").value.trim()   || null,
        status:      document.getElementById("proj-status").value,
        sort_order:  parseInt(document.getElementById("proj-order").value) || 0,
        featured:    document.getElementById("proj-featured").checked ? 1 : 0,
    };

    try {
        if (id) {
            await updateProject(id, data);
            showToast("Project updated!");
        } else {
            await createProject(data);
            showToast("Project created!");
        }
        projectFormWrap.classList.add("hidden");
        projectForm.reset();
        loadAdminProjects();
    } catch (err) {
        projectFormError.textContent = err.message;
        projectFormError.classList.remove("hidden");
    }
});

// ── Utilities ──────────────────────────────────────────────────────────────

function setLoading(section, loading) {
    document.getElementById(`${section}-loading`).classList.toggle("hidden", !loading);
}

function showToast(message, type = "success") {
    adminToast.textContent = message;
    adminToast.className = `toast toast-${type}`;
    adminToast.classList.remove("hidden");
    setTimeout(() => adminToast.classList.add("hidden"), 3500);
}

function escHtml(str) {
    return String(str ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function slugify(str) {
    return str.toLowerCase().replace(/\s+/g, "-");
}

function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString("en-PH", {
        year: "numeric", month: "short", day: "numeric",
    });
}

function updateStats() {
    if (statUnreadCount) {
        const unread = loadedMessages.filter((m) => !m.is_read).length;
        animateNumberValue(statUnreadCount, unread);
    }
    if (statProjectsCount) {
        animateNumberValue(statProjectsCount, loadedProjects.length);
    }
    if (statCompletedCount) {
        const completed = loadedProjects.filter((p) => p.status === "Completed" || p.status === "Live").length;
        animateNumberValue(statCompletedCount, completed);
    }
}

function animateNumberValue(el, target) {
    const start = parseInt(el.textContent) || 0;
    if (start === target) return;
    const duration = 400; // ms duration
    const startTime = performance.now();
    
    function update(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const ease = progress * (2 - progress); // Ease out quadratic
        const current = Math.floor(start + (target - start) * ease);
        el.textContent = current;
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            el.textContent = target;
        }
    }
    requestAnimationFrame(update);
}

function showConfirm(title, message) {
    return new Promise((resolve) => {
        confirmTitle.textContent = title;
        confirmMessage.textContent = message;
        confirmModal.classList.remove("hidden");
        
        function handleCancel() {
            cleanup();
            resolve(false);
        }
        
        function handleConfirm() {
            cleanup();
            resolve(true);
        }
        
        function cleanup() {
            confirmBtnCancel.removeEventListener("click", handleCancel);
            confirmBtnOk.removeEventListener("click", handleConfirm);
            confirmModal.classList.add("hidden");
        }
        
        confirmBtnCancel.addEventListener("click", handleCancel);
        confirmBtnOk.addEventListener("click", handleConfirm);
    });
}

// ── Boot ───────────────────────────────────────────────────────────────────
init();
