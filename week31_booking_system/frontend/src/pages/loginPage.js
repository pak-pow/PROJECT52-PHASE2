import { renderNavbar } from "../components/navbar.js";
import { apiLogin } from "../api/authApi.js";
import { showToast } from "../utils/helpers.js";

document.addEventListener("DOMContentLoaded", () => {
    renderNavbar();

    const form = document.getElementById("login-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const usernameInput = document.getElementById("username");
        const passwordInput = document.getElementById("password");

        const username = usernameInput ? usernameInput.value.trim() : "";
        const password = passwordInput ? passwordInput.value : "";

        try {
            await apiLogin(username, password);
            showToast("Login successful!", "success");
            setTimeout(() => {
                window.location.href = "index.html";
            }, 500);
        } catch (err) {
            showToast(err.message, "error");
        }
    });
});
