import { renderNavbar } from "../components/navbar.js";
import { sendBurstRequest, issueApiKey } from "../api/limiterApi.js";
import { showToast, escapeHtml } from "../utils/helpers.js";
import { getActiveApiKey, setActiveApiKey } from "../utils/authCheck.js";

document.addEventListener("DOMContentLoaded", () => {
    renderNavbar("dashboard");

    let currentApiKey = getActiveApiKey();
    let currentTier = "free";
    let currentAlgorithm = "token_bucket";

    // Day 4 Analytics State
    let totalReqs = 0;
    let acceptedReqs = 0;
    let blockedReqs = 0;

    const activeKeyText = document.getElementById("active-key-text");
    const remainingCount = document.getElementById("remaining-count");
    const limitTotal = document.getElementById("limit-total");
    const capacityFill = document.getElementById("capacity-fill");
    const bucketStatus = document.getElementById("bucket-status");
    const responseLogBody = document.getElementById("response-log-body");

    // Analytics Scorecard Elements
    const statTotalReqs = document.getElementById("stat-total-reqs");
    const statAcceptedReqs = document.getElementById("stat-accepted-reqs");
    const statBlockedReqs = document.getElementById("stat-blocked-reqs");
    const statAcceptanceRate = document.getElementById("stat-acceptance-rate");

    if (activeKeyText) activeKeyText.textContent = currentApiKey;

    // Day 4: Algorithm Toggle Buttons
    document.querySelectorAll(".algo-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".algo-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentAlgorithm = btn.getAttribute("data-algo");
            const label = currentAlgorithm === "token_bucket" ? "Token Bucket" : "Sliding Window Log";
            showToast(`Switched rate limiter engine to ${label}.`, "info");
        });
    });

    // Tier Selector Buttons
    document.querySelectorAll(".tier-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
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

    // Clear Console & Reset Stats Button
    document.getElementById("clear-console-btn")?.addEventListener("click", () => {
        totalReqs = 0;
        acceptedReqs = 0;
        blockedReqs = 0;

        if (statTotalReqs) statTotalReqs.textContent = "0";
        if (statAcceptedReqs) statAcceptedReqs.textContent = "0";
        if (statBlockedReqs) statBlockedReqs.textContent = "0";
        if (statAcceptanceRate) statAcceptanceRate.textContent = "100%";

        if (responseLogBody) {
            responseLogBody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">
                        Console cleared. Click a burst button above to send live API traffic!
                    </td>
                </tr>
            `;
        }
        showToast("Inspection console & stats scorecard reset.", "info");
    });

    // Update Analytics Scorecard
    function updateAnalytics(isOk) {
        totalReqs++;
        if (isOk) acceptedReqs++;
        else blockedReqs++;

        if (statTotalReqs) statTotalReqs.textContent = totalReqs;
        if (statAcceptedReqs) statAcceptedReqs.textContent = acceptedReqs;
        if (statBlockedReqs) statBlockedReqs.textContent = blockedReqs;

        const rate = totalReqs > 0 ? Math.round((acceptedReqs / totalReqs) * 100) : 100;
        if (statAcceptanceRate) statAcceptanceRate.textContent = `${rate}%`;
    }

    // Helper: Add log row to console table
    function logResponse(status, endpoint, headers) {
        if (!responseLogBody) return;

        // Clear empty state row
        if (responseLogBody.querySelector("td[colspan='5']")) {
            responseLogBody.innerHTML = "";
        }

        const isOk = status === 200;
        updateAnalytics(isOk);

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
        const algoTag = currentAlgorithm === "token_bucket" ? "[Token Bucket]" : "[Sliding Window]";
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${nowStr}</td>
            <td>${escapeHtml(endpoint)} <span style="font-size: 0.75rem; color: var(--text-muted);">${algoTag}</span></td>
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
    async function fireBurst(count) {
        const endpoint = currentAlgorithm === "token_bucket" ? "/tier/data" : "/sliding/test";
        showToast(`Firing ${count}x burst requests using ${currentAlgorithm.replace('_', ' ')}...`, "info");
        
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

    // Day 5: Custom Sandbox Test Handler
    document.getElementById("fire-custom-sandbox-btn")?.addEventListener("click", async () => {
        const cLimit = parseInt(document.getElementById("custom-limit-input")?.value || "3");
        const cWindow = parseFloat(document.getElementById("custom-window-input")?.value || "5");

        if (isNaN(cLimit) || cLimit < 1 || isNaN(cWindow) || cWindow < 1) {
            showToast("Please enter valid positive numbers for limit and window.", "warning");
            return;
        }

        const endpoint = "/custom/test";
        showToast(`Testing Custom Sandbox Limit (${cLimit} reqs / ${cWindow}s)...`, "info");
        try {
            const res = await sendBurstRequest(endpoint, currentApiKey, {
                custom_limit: cLimit,
                custom_window: cWindow
            });
            logResponse(res.status, `${endpoint}?limit=${cLimit}&win=${cWindow}s`, res.headers);
        } catch (err) {
            logResponse(500, endpoint, { remaining: 0, limit: 0, retryAfter: null });
        }
    });
});
