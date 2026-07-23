/**
 * main.js — SocialFeed application entry point.
 * Bootstraps authentication, routing, and component initialization.
 */
import { getSessionUser, saveSession, clearSession, apiLogin, apiRegister, apiLogout } from "./api/authApi.js";
import { avatarUrl } from "./api/userApi.js";
import { getCurrentUser, setCurrentUser } from "./utils/state.js";
import { showPage, initRouter } from "./router.js";
import { initCompose } from "./components/compose.js";
import { loadSuggestions } from "./components/suggestions.js";
import { loadFeed, resetFeed, setupFeedInfiniteScroll } from "./pages/feed.js";
import { loadExplore, resetExplore, loadExploreByTag, setupExplorePage } from "./pages/explore.js";
import { loadProfile } from "./pages/profile.js";

// ── DOM References ─────────────────────────────────────────
const authScreen         = document.getElementById("auth-screen");
const mainApp            = document.getElementById("main-app");
const loginForm          = document.getElementById("login-form");
const registerForm       = document.getElementById("register-form");
const loginError         = document.getElementById("login-error");
const registerError      = document.getElementById("register-error");
const logoutBtn          = document.getElementById("logout-btn");
const sidebarDisplayName = document.getElementById("sidebar-display-name");
const sidebarUsername    = document.getElementById("sidebar-username");
const sidebarAvatar      = document.getElementById("sidebar-avatar");
const composeAvatar      = document.getElementById("compose-avatar");
const composeInput       = document.getElementById("compose-input");

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
    loginError.classList.add("hidden");
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;
    const btn = document.getElementById("login-submit");
    btn.disabled = true; btn.textContent = "Logging in…";
    const { ok, data } = await apiLogin(username, password);
    btn.disabled = false; btn.textContent = "Login";
    if (!ok) { loginError.textContent = data.error || "Login failed."; loginError.classList.remove("hidden"); return; }
    saveSession(data.token, data.username, data.display_name, data.avatar_path);
    bootApp();
});

// ── Auth: Register ─────────────────────────────────────────
registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    registerError.classList.add("hidden");
    const username    = document.getElementById("reg-username").value.trim();
    const displayName = document.getElementById("reg-display").value.trim();
    const password    = document.getElementById("reg-password").value;
    const btn = document.getElementById("register-submit");
    btn.disabled = true; btn.textContent = "Creating…";
    const { ok, data } = await apiRegister(username, displayName, password);
    btn.disabled = false; btn.textContent = "Create Account";
    if (!ok) { registerError.textContent = data.error || "Registration failed."; registerError.classList.remove("hidden"); return; }
    saveSession(data.token, data.username, data.display_name, "");
    bootApp();
});

// ── Auth: Logout ───────────────────────────────────────────
logoutBtn.addEventListener("click", async () => {
    await apiLogout();
    clearSession();
    setCurrentUser(null);
    showAuth();
});

function showAuth() {
    authScreen.classList.remove("hidden");
    mainApp.classList.add("hidden");
}

// ── Application Boot ──────────────────────────────────────
function bootApp() {
    const user = getSessionUser();
    if (!user) { showAuth(); return; }
    setCurrentUser(user);

    authScreen.classList.add("hidden");
    mainApp.classList.remove("hidden");

    // Populate sidebar
    if (sidebarDisplayName) sidebarDisplayName.textContent = user.displayName;
    if (sidebarUsername)    sidebarUsername.textContent    = `@${user.username}`;
    if (sidebarAvatar)      sidebarAvatar.textContent      = (user.displayName || user.username)[0].toUpperCase();
    if (composeAvatar)      composeAvatar.textContent      = (user.displayName || user.username)[0].toUpperCase();

    // Sidebar avatar image
    if (sidebarAvatar) {
        const sAvImg = new Image();
        sAvImg.onload = () => {
            sidebarAvatar.textContent = "";
            sidebarAvatar.style.cssText = `background-image:url(${sAvImg.src});background-size:cover;background-position:center;`;
        };
        sAvImg.src = avatarUrl(user.username);
    }

    // Sidebar compose button
    const sidebarComposeBtn = document.getElementById("sidebar-compose-btn");
    if (sidebarComposeBtn) {
        sidebarComposeBtn.addEventListener("click", () => {
            showPage("feed");
            if (composeInput) composeInput.focus();
        });
    }

    // Initialize modules
    initRouter({
        onNavigate: ({ page, alreadyOnPage, user }) => {
            if (page === "profile") {
                loadProfile(user?.username);
            } else {
                showPage(page);
                if (page === "feed") {
                    if (alreadyOnPage) {
                        window.scrollTo({ top: 0, behavior: "smooth" });
                    } else {
                        resetFeed(); loadFeed();
                    }
                }
                if (page === "explore") { resetExplore(); loadExplore(); }
            }
        }
    });
    initCompose();
    setupFeedInfiniteScroll();
    setupExplorePage();

    resetFeed();
    showPage("feed");
    loadFeed();
    loadSuggestions();
}

// ── @mention & #hashtag delegated click ───────────────
document.addEventListener("click", (e) => {
    const mention = e.target.closest(".mention");
    if (mention) {
        e.preventDefault();
        const username = mention.textContent.replace(/^@/, "").trim();
        if (username) loadProfile(username);
        return;
    }
    const hashtag = e.target.closest(".hashtag");
    if (hashtag) {
        e.preventDefault();
        const tag = hashtag.textContent.replace(/^#/, "").trim();
        if (tag) loadExploreByTag(tag);
    }
});

// ── Boot ──────────────────────────────────────────────
bootApp();
