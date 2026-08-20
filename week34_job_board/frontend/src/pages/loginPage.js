import { renderNavbar } from "../components/navbar.js";
import { loginUser } from "../api/authApi.js";
import { setStoredUser } from "../utils/authCheck.js";
import { showToast } from "../utils/helpers.js";

document.addEventListener("DOMContentLoaded", () => {
    renderNavbar("login");

    const loginForm = document.getElementById("login-form");

    loginForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById("login-submit-btn");
        if (submitBtn) submitBtn.disabled = true;

        const email = document.getElementById("login-email").value.trim();
        const password = document.getElementById("login-password").value.trim();

        try {
            showToast("Signing in...", "info");
            const data = await loginUser(email, password);
            setStoredUser(data.user);
            showToast(`Welcome back, ${data.user.username}! 👋`, "success");

            setTimeout(() => {
                if (data.user.role === "employer") {
                    window.location.href = "employer.html";
                } else {
                    window.location.href = "dashboard.html";
                }
            }, 500);
        } catch (err) {
            showToast(err.message || "Login failed.", "error");
        } finally {
            if (submitBtn) submitBtn.disabled = false;
        }
    });
});
