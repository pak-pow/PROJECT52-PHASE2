import { renderNavbar } from "../components/navbar.js";
import { issueApiKey } from "../api/limiterApi.js";
import { showToast } from "../utils/helpers.js";
import { setActiveApiKey, clearSession } from "../utils/authCheck.js";

document.addEventListener("DOMContentLoaded", () => {
    renderNavbar("login");

    const loginForm = document.getElementById("login-form");
    loginForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const tier = document.getElementById("tier-select")?.value || "free";

        try {
            showToast("Issuing new developer API key...", "info");
            const res = await issueApiKey(tier);
            if (res.api_key) {
                setActiveApiKey(res.api_key);
                showToast(`Success! Key issued for ${tier.toUpperCase()} tier. Redirecting...`, "success");
                setTimeout(() => {
                    window.location.href = "index.html";
                }, 1200);
            }
        } catch (err) {
            showToast("Failed to issue API key. Make sure backend is running.", "error");
        }
    });
});
