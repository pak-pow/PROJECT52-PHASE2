/**
 * main.js — SocialFeed application entry point.
 * Bootstraps auth state and wires up all page navigation.
 */
import { getSessionUser, saveSession, clearSession, apiLogin, apiRegister, apiLogout } from "./api/authApi.js";
import { apiFeed, apiExplore, apiCreatePost, apiLikePost, apiDeletePost } from "./api/postApi.js";
import { showToast, navigate, relativeTime, escapeHtml, linkifyContent, formatCount } from "./utils/helpers.js";

// ── DOM References ─────────────────────────────────────────
const authScreen   = document.getElementById("auth-screen");
const mainApp      = document.getElementById("main-app");
const loginForm    = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const loginError   = document.getElementById("login-error");
const registerError = document.getElementById("register-error");
const logoutBtn    = document.getElementById("logout-btn");
const sidebarDisplayName = document.getElementById("sidebar-display-name");
const sidebarUsername    = document.getElementById("sidebar-username");
const sidebarAvatar      = document.getElementById("sidebar-avatar");
const composeAvatar      = document.getElementById("compose-avatar");
const composeInput       = document.getElementById("compose-input");
const composeSubmit      = document.getElementById("compose-submit-btn");
const charCounter        = document.getElementById("char-counter");
const feedList           = document.getElementById("feed-list");
const exploreList        = document.getElementById("explore-list");

// ── Tab switching (Login / Register) ───────────────────────
document.querySelectorAll(".auth-tab").forEach(tab => {
    tab.addEventListener("click", () => {
        document.querySelectorAll(".auth-tab").forEach(t => {
            t.classList.toggle("active", t === tab);
            t.setAttribute("aria-selected", t === tab);
        });
        const target = tab.dataset.target;
        ["login-form", "register-form"].forEach(id => {
            document.getElementById(id).classList.toggle("hidden", id !== target);
        });
    });
});

// ── Auth: Login ────────────────────────────────────────────
loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;
    const btn = document.getElementById("login-submit");
    btn.disabled = true;
    btn.textContent = "Logging in…";
    const { ok, data } = await apiLogin(username, password);
    btn.disabled = false;
    btn.textContent = "Login";
    if (!ok) {
        loginError.textContent = data.error || "Login failed.";
        loginError.classList.remove("hidden");
        return;
    }
    saveSession(data.token, data.username, data.display_name, data.avatar_path);
    bootApp();
});

// ── Auth: Register ─────────────────────────────────────────
registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username    = document.getElementById("reg-username").value.trim();
    const displayName = document.getElementById("reg-display").value.trim();
    const password    = document.getElementById("reg-password").value;
    const btn = document.getElementById("register-submit");
    btn.disabled = true;
    btn.textContent = "Creating…";
    const { ok, data } = await apiRegister(username, displayName, password);
    btn.disabled = false;
    btn.textContent = "Create Account";
    if (!ok) {
        registerError.textContent = data.error || "Registration failed.";
        registerError.classList.remove("hidden");
        return;
    }
    saveSession(data.token, data.username, data.display_name, "");
    bootApp();
});

// ── Auth: Logout ───────────────────────────────────────────
logoutBtn.addEventListener("click", async () => {
    await apiLogout();
    clearSession();
    showAuth();
});

// ── Page navigation ────────────────────────────────────────
const pages = ["feed", "explore", "profile", "post-detail"];

function showPage(name) {
    pages.forEach(p => {
        document.getElementById(`page-${p}`)?.classList.toggle("hidden", p !== name);
        document.getElementById(`page-${p}`)?.classList.toggle("active", p === name);
    });
    document.querySelectorAll(".nav-item").forEach(el => {
        el.classList.toggle("active", el.dataset.page === name);
    });
}

document.querySelectorAll(".nav-item").forEach(el => {
    el.addEventListener("click", (e) => {
        e.preventDefault();
        const page = el.dataset.page;
        showPage(page);
        if (page === "feed") loadFeed();
        if (page === "explore") loadExplore();
    });
});

// ── Compose: char counter ──────────────────────────────────
composeInput.addEventListener("input", () => {
    charCounter.textContent = 280 - composeInput.value.length;
    charCounter.classList.toggle("char-danger", composeInput.value.length > 260);
});

// ── Compose: post submit ───────────────────────────────────
composeSubmit.addEventListener("click", async () => {
    const content = composeInput.value.trim();
    const imageFile = document.getElementById("compose-image-input").files[0] || null;
    if (!content && !imageFile) return;
    composeSubmit.disabled = true;
    composeSubmit.textContent = "Posting…";
    const { ok, data } = await apiCreatePost(content, imageFile);
    composeSubmit.disabled = false;
    composeSubmit.textContent = "Post";
    if (!ok) { showToast(data.error || "Could not post.", "error"); return; }
    composeInput.value = "";
    charCounter.textContent = "280";
    document.getElementById("compose-image-input").value = "";
    showToast("Posted! 🎉", "success");
    loadFeed();
});

// ── Render post card ───────────────────────────────────────
function renderPostCard(post) {
    const card = document.createElement("article");
    card.className = "post-card";
    card.dataset.postId = post.id;

    const initials = (post.display_name || post.username || "?")[0].toUpperCase();
    card.innerHTML = `
        <div class="post-avatar avatar avatar-md">${initials}</div>
        <div class="post-body">
            <div class="post-header">
                <a class="post-display-name" href="#" data-username="${escapeHtml(post.username)}">${escapeHtml(post.display_name)}</a>
                <span class="post-username">@${escapeHtml(post.username)}</span>
                <span class="post-time">${relativeTime(post.created_at)}</span>
            </div>
            <div class="post-content">${linkifyContent(post.content)}</div>
            <div class="post-actions">
                <button class="action-btn like-btn ${post.liked_by_me ? 'liked' : ''}" data-post-id="${post.id}" aria-label="Like post">
                    ${post.liked_by_me ? "❤️" : "🤍"} <span class="like-count">${formatCount(post.like_count)}</span>
                </button>
                <button class="action-btn reply-btn" data-post-id="${post.id}" aria-label="Reply">
                    💬 <span>${formatCount(post.reply_count)}</span>
                </button>
                <button class="action-btn repost-btn" data-post-id="${post.id}" aria-label="Repost">
                    🔁 <span>${formatCount(post.repost_count)}</span>
                </button>
            </div>
        </div>
    `;

    // Like handler (optimistic UI)
    card.querySelector(".like-btn").addEventListener("click", async (e) => {
        const btn = e.currentTarget;
        const wasLiked = btn.classList.contains("liked");
        const countEl = btn.querySelector(".like-count");
        const currentCount = parseInt(countEl.textContent.replace(/[KM]/g, "")) || 0;

        // Optimistic update
        btn.classList.toggle("liked", !wasLiked);
        btn.innerHTML = `${!wasLiked ? "❤️" : "🤍"} <span class="like-count">${formatCount(wasLiked ? Math.max(0, currentCount - 1) : currentCount + 1)}</span>`;

        const { ok, data } = await apiLikePost(post.id);
        if (ok) {
            btn.innerHTML = `${data.liked ? "❤️" : "🤍"} <span class="like-count">${formatCount(data.count)}</span>`;
            btn.classList.toggle("liked", data.liked);
        } else {
            // Rollback
            btn.classList.toggle("liked", wasLiked);
            btn.innerHTML = `${wasLiked ? "❤️" : "🤍"} <span class="like-count">${formatCount(currentCount)}</span>`;
        }
    });

    return card;
}

// ── Load home feed ─────────────────────────────────────────
async function loadFeed() {
    feedList.innerHTML = '<div class="skeleton-list">' + Array(5).fill('<div class="skeleton-card"></div>').join("") + '</div>';
    const posts = await apiFeed();
    feedList.innerHTML = "";
    if (!posts.length) {
        feedList.innerHTML = '<p class="empty-state">No posts yet. Follow some people or write your first post!</p>';
        return;
    }
    posts.forEach(p => feedList.appendChild(renderPostCard(p)));
}

// ── Load explore feed ──────────────────────────────────────
async function loadExplore() {
    exploreList.innerHTML = '<div class="skeleton-list">' + Array(5).fill('<div class="skeleton-card"></div>').join("") + '</div>';
    const posts = await apiExplore();
    exploreList.innerHTML = "";
    if (!posts.length) {
        exploreList.innerHTML = '<p class="empty-state">Nothing trending yet. Be the first to post!</p>';
        return;
    }
    posts.forEach(p => exploreList.appendChild(renderPostCard(p)));
}

// ── Show auth vs app ───────────────────────────────────────
function showAuth() {
    authScreen.classList.remove("hidden");
    mainApp.classList.add("hidden");
}

function bootApp() {
    const user = getSessionUser();
    if (!user) { showAuth(); return; }

    authScreen.classList.add("hidden");
    mainApp.classList.remove("hidden");

    // Populate sidebar user info
    sidebarDisplayName.textContent = user.displayName;
    sidebarUsername.textContent = `@${user.username}`;
    sidebarAvatar.textContent = (user.displayName || user.username)[0].toUpperCase();
    composeAvatar.textContent = (user.displayName || user.username)[0].toUpperCase();

    showPage("feed");
    loadFeed();
}

// ── Boot on load ───────────────────────────────────────────
bootApp();
