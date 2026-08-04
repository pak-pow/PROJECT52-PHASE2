import { renderNavbar } from "../components/navbar.js";
import { issueApiKey } from "../api/limiterApi.js";
import { showToast } from "../utils/helpers.js";
import { setActiveApiKey } from "../utils/authCheck.js";

document.addEventListener("DOMContentLoaded", () => {
    renderNavbar("register");

    const registerForm = document.getElementById("register-form");
    registerForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const tier = document.getElementById("reg-tier")?.value || "free";

        try {
            showToast("Registering account & issuing API key...", "info");
            const res = await issueApiKey(tier);
            if (res.api_key) {
                setActiveApiKey(res.api_key);
                showToast(`Developer registered! Key issued for ${tier.toUpperCase()} tier. Redirecting...`, "success");
                setTimeout(() => {
                    window.location.href = "index.html";
                }, 1200);
            }
        } catch (err) {
            showToast("Failed to complete registration.", "error");
        }
    });
});
