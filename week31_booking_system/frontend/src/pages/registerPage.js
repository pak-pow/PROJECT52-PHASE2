import { renderNavbar } from "../components/navbar.js";
import { apiRegister } from "../api/authApi.js";
import { showToast } from "../utils/helpers.js";

document.addEventListener("DOMContentLoaded", () => {
    renderNavbar();

    const form = document.getElementById("register-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const usernameInput = document.getElementById("username");
        const displayNameInput = document.getElementById("display_name");
        const emailInput = document.getElementById("email");
        const passwordInput = document.getElementById("password");

        const username = usernameInput ? usernameInput.value.trim() : "";
        const display_name = displayNameInput ? displayNameInput.value.trim() : "";
        const email = emailInput ? emailInput.value.trim() : "";
        const password = passwordInput ? passwordInput.value : "";

        try {
            await apiRegister(username, display_name, email, password);
            showToast("Account created successfully!", "success");
            setTimeout(() => {
                window.location.href = "index.html";
            }, 500);
        } catch (err) {
            showToast(err.message, "error");
        }
    });
});
