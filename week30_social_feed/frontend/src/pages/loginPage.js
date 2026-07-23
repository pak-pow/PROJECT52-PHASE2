/**
 * loginPage.js — Login page controller.
 */
import { apiLogin, saveSession } from "../api/authApi.js";
import { requireGuestPage } from "../utils/authCheck.js";

requireGuestPage();

const loginForm  = document.getElementById("login-form");
const loginError = document.getElementById("login-error");

if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        loginError.classList.add("hidden");
        const username = document.getElementById("login-username").value.trim();
        const password = document.getElementById("login-password").value;
        const btn = document.getElementById("login-submit");
        btn.disabled = true; btn.textContent = "Logging in…";
        
        const { ok, data } = await apiLogin(username, password);
        btn.disabled = false; btn.textContent = "Login";
        
        if (!ok) {
            loginError.textContent = data.error || "Login failed.";
            loginError.classList.remove("hidden");
            return;
        }
        
        saveSession(data.token, data.username, data.display_name, data.avatar_path);
        window.location.href = "feed.html";
    });
}
