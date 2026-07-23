/**
 * registerPage.js — Registration page controller.
 */
import { apiRegister, saveSession } from "../api/authApi.js";
import { requireGuestPage } from "../utils/authCheck.js";

await requireGuestPage();

const registerForm  = document.getElementById("register-form");
const registerError = document.getElementById("register-error");

if (registerForm) {
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
        
        if (!ok) {
            registerError.textContent = data.error || "Registration failed.";
            registerError.classList.remove("hidden");
            return;
        }
        
        saveSession(data.token, data.username, data.display_name, "");
        window.location.href = "feed.html";
    });
}
