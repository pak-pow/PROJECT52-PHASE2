import { renderNavbar } from "../components/navbar.js";
import { sendBurstRequest, issueApiKey } from "../api/limiterApi.js";
import { showToast, escapeHtml } from "../utils/helpers.js";
import { getActiveApiKey, setActiveApiKey } from "../utils/authCheck.js";

document.addEventListener("DOMContentLoaded", () => {
    renderNavbar("dashboard");

    let currentApiKey = getActiveApiKey();
    let currentTier = "free";

    const activeKeyText = document.getElementById("active-key-text");
    const remainingCount = document.getElementById("remaining-count");
    const limitTotal = document.getElementById("limit-total");
    const capacityFill = document.getElementById("capacity-fill");
    const bucketStatus = document.getElementById("bucket-status");
    const responseLogBody = document.getElementById("response-log-body");

    if (activeKeyText) activeKeyText.textContent = currentApiKey;

    // Tier Selector Buttons
    document.querySelectorAll(".tier-btn").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            document.querySelectorAll(".tier-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            currentTier = btn.getAttribute("data-tier");
            showToast(`Selected ${currentTier.toUpperCase()} tier. Generating API key...`, "info");

            try {
                const res = await issueApiKey(currentTier);
                if (res.api_key) {
                    currentApiKey = res.api_key;
                    setActiveApiKey(currentApiKey);
                    if (activeKeyText) activeKeyText.textContent = currentApiKey;
                    showToast(`Active API Key updated: ${currentApiKey}`, "success");
                }
            } catch (err) {
                showToast("Failed to issue API key.", "error");
            }
        });
    });

    // Issue New Key Button
    document.getElementById("generate-key-btn")?.addEventListener("click", async () => {
        try {
            const res = await issueApiKey(currentTier);
            if (res.api_key) {
                currentApiKey = res.api_key;
                setActiveApiKey(currentApiKey);
                if (activeKeyText) activeKeyText.textContent = currentApiKey;
                showToast(`Issued new key: ${currentApiKey}`, "success");
            }
        } catch (err) {
            showToast("Failed to generate key.", "error");
        }
    });

    // Helper: Add log row to console table
    function logResponse(status, endpoint, headers) {
        if (!responseLogBody) return;

        // Clear empty state row
        if (responseLogBody.querySelector("td[colspan='5']")) {
            responseLogBody.innerHTML = "";
        }

        const isOk = status === 200;
        const remaining = headers.remaining !== null ? headers.remaining : "--";
        const limit = headers.limit !== null ? headers.limit : "--";
        const retryAfter = headers.retryAfter ? `${headers.retryAfter}s` : "--";

        // Update Gauge Meter
        if (limitTotal && limit !== "--") limitTotal.textContent = limit;
        if (remainingCount && remaining !== "--") remainingCount.textContent = remaining;

        if (remaining !== "--" && limit !== "--" && parseInt(limit) > 0) {
            const pct = Math.max(0, Math.min(100, (parseInt(remaining) / parseInt(limit)) * 100));
            if (capacityFill) {
                capacityFill.style.width = `${pct}%`;
                if (pct <= 20) {
                    capacityFill.classList.add("warning");
                } else {
                    capacityFill.classList.remove("warning");
                }
            }
        }

        if (bucketStatus) {
            if (isOk) {
                bucketStatus.textContent = "READY";
                bucketStatus.style.color = "var(--success)";
            } else {
                bucketStatus.textContent = "RATE LIMITED (429)";
                bucketStatus.style.color = "var(--danger)";
            }
        }

        const nowStr = new Date().toLocaleTimeString();
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${nowStr}</td>
            <td>${escapeHtml(endpoint)}</td>
            <td>
                <span class="status-badge ${isOk ? 'ok' : 'blocked'}">
                    ${status} ${isOk ? 'OK' : 'TOO MANY REQUESTS'}
                </span>
            </td>
            <td>${remaining} / ${limit}</td>
            <td style="color: ${retryAfter !== '--' ? 'var(--danger)' : 'var(--text-muted)'}; font-weight: bold;">
                ${retryAfter}
            </td>
        `;

        responseLogBody.prepend(tr);
    }

    // Burst Execution Helper
    async function fireBurst(count, endpoint = "/tier/data") {
        showToast(`Firing ${count}x burst requests to ${endpoint}...`, "info");
        for (let i = 0; i < count; i++) {
            try {
                const res = await sendBurstRequest(endpoint, currentApiKey);
                logResponse(res.status, endpoint, res.headers);
            } catch (err) {
                logResponse(500, endpoint, { remaining: 0, limit: 0, retryAfter: null });
            }
        }
    }

    // Attach Event Listeners
    document.getElementById("burst-1-btn")?.addEventListener("click", () => fireBurst(1));
    document.getElementById("burst-5-btn")?.addEventListener("click", () => fireBurst(5));
    document.getElementById("burst-10-btn")?.addEventListener("click", () => fireBurst(10));
});
