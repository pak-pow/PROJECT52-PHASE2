import { renderNavbar } from "../components/navbar.js";
import { renderLogCard } from "../components/logCard.js";
import { initTheme } from "../utils/theme.js";
import { showToast } from "../utils/helpers.js";
import {
    checkServerHealth,
    sendNotification,
    fetchTemplates,
    fetchUserPreferences,
    updateUserPreferences,
    fetchUserNotifications
} from "../api/notificationApi.js";

let allTemplates = [];

document.addEventListener("DOMContentLoaded", async () => {
    initTheme();

    // 1. Initial Health Check
    const isOnline = await checkServerHealth();
    renderNavbar(isOnline);

    if (!isOnline) {
        showToast("Backend server offline. Please start 'python run.py' on port 5000.", "warning");
    }

    // 2. Setup Channel Selector Buttons
    const channelButtons = document.querySelectorAll(".channel-pill-btn");
    const channelInput = document.getElementById("selected-channel");
    const recipientLabel = document.getElementById("recipient-label");
    const recipientInput = document.getElementById("input-recipient");

    channelButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            channelButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            const channel = btn.getAttribute("data-channel");
            channelInput.value = channel;

            // Update placeholders
            if (channel === "email") {
                recipientLabel.textContent = "Recipient Email Address";
                recipientInput.placeholder = "vee@dev.io";
            } else if (channel === "sms") {
                recipientLabel.textContent = "Recipient Phone Number (E.164)";
                recipientInput.placeholder = "+14155552671";
            } else if (channel === "webhook") {
                recipientLabel.textContent = "Target Webhook URL";
                recipientInput.placeholder = "https://api.myapp.com/webhook";
            }

            filterTemplatesByChannel(channel);
        });
    });

    // 3. Load Templates
    const templateSelect = document.getElementById("select-template");
    const variablesContainer = document.getElementById("variables-container");
    const directContentContainer = document.getElementById("direct-content-container");
    const variablesInput = document.getElementById("input-variables");

    async function loadTemplates() {
        try {
            allTemplates = await fetchTemplates();
            filterTemplatesByChannel(channelInput.value);
        } catch {
            // Server offline fallback
        }
    }

    function filterTemplatesByChannel(channel) {
        templateSelect.innerHTML = `<option value="">-- Custom Direct Message --</option>`;
        const matching = allTemplates.filter(t => t.channel === channel);

        matching.forEach(t => {
            const opt = document.createElement("option");
            opt.value = t.name;
            opt.textContent = `${t.name} ${t.subject ? `(${t.subject})` : ''}`;
            templateSelect.appendChild(opt);
        });

        toggleTemplateInputs();
    }

    templateSelect?.addEventListener("change", toggleTemplateInputs);

    function toggleTemplateInputs() {
        const selected = templateSelect.value;
        if (selected) {
            variablesContainer.style.display = "flex";
            directContentContainer.style.display = "none";

            // Prefill sample variables for selected template
            if (selected === "welcome_email") {
                variablesInput.value = JSON.stringify({ username: "Vee", email: "vee@dev.io" }, null, 2);
            } else if (selected === "job_application_submitted") {
                variablesInput.value = JSON.stringify({ applicant_name: "Vee", job_title: "Senior Backend Engineer", company: "TechJobs Corp" }, null, 2);
            } else if (selected === "security_alert_sms") {
                variablesInput.value = JSON.stringify({ username: "vee_user", location: "San Francisco, CA", time: "16:20 UTC" }, null, 2);
            } else if (selected === "application_status_webhook") {
                variablesInput.value = JSON.stringify({ app_id: 101, status: "Interviewing", user_id: 1 }, null, 2);
            } else {
                variablesInput.value = "{}";
            }
        } else {
            variablesContainer.style.display = "none";
            directContentContainer.style.display = "flex";
        }
    }

    // 4. User Preferences Handling
    const userIdInput = document.getElementById("input-user-id");
    const prefUserDisplay = document.getElementById("pref-user-display");
    const emailToggle = document.getElementById("pref-email-toggle");
    const smsToggle = document.getElementById("pref-sms-toggle");
    const webhookToggle = document.getElementById("pref-webhook-toggle");

    async function loadUserPreferences(userId) {
        try {
            if (prefUserDisplay) prefUserDisplay.textContent = userId;
            const prefs = await fetchUserPreferences(userId);
            if (emailToggle) emailToggle.checked = prefs.email_enabled;
            if (smsToggle) smsToggle.checked = prefs.sms_enabled;
            if (webhookToggle) webhookToggle.checked = prefs.webhook_enabled;
        } catch {
            // Ignore
        }
    }

    userIdInput?.addEventListener("change", () => {
        loadUserPreferences(userIdInput.value);
        loadFeed();
    });

    [emailToggle, smsToggle, webhookToggle].forEach(toggle => {
        toggle?.addEventListener("change", async () => {
            const userId = parseInt(userIdInput.value || 1);
            try {
                await updateUserPreferences(userId, {
                    email_enabled: emailToggle.checked,
                    sms_enabled: smsToggle.checked,
                    webhook_enabled: webhookToggle.checked
                });
                showToast("Preferences updated successfully! 🛡️", "success");
            } catch (err) {
                showToast(err.message || "Failed to update preferences.", "error");
            }
        });
    });

    // 5. Send Notification Form Submission
    const dispatchForm = document.getElementById("dispatch-form");
    const sendBtn = document.getElementById("send-notif-btn");

    dispatchForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        sendBtn.disabled = true;

        const channel = channelInput.value;
        const userId = parseInt(userIdInput.value || 1);
        const recipient = recipientInput.value.trim();
        const idempotencyKey = document.getElementById("input-idempotency").value.trim() || undefined;
        const templateName = templateSelect.value || undefined;

        let variables = {};
        if (templateName) {
            try {
                variables = JSON.parse(variablesInput.value || "{}");
            } catch {
                showToast("Invalid JSON format in template variables.", "error");
                sendBtn.disabled = false;
                return;
            }
        }

        const directContent = document.getElementById("input-content").value.trim() || undefined;

        const payload = {
            user_id: userId,
            recipient: recipient,
            channel: channel,
            template_name: templateName,
            variables: variables,
            content: directContent,
            idempotency_key: idempotencyKey
        };

        try {
            const res = await sendNotification(payload);
            showToast(res.message || "Notification enqueued! 🚀", "success");
            setTimeout(loadFeed, 350); // Refresh feed after queue execution
        } catch (err) {
            showToast(err.message || "Failed to dispatch notification.", "error");
        } finally {
            sendBtn.disabled = false;
        }
    });

    // 6. Live Audit Feed & Metrics
    const auditContainer = document.getElementById("audit-feed-container");
    const refreshBtn = document.getElementById("refresh-logs-btn");
    const metricTotal = document.getElementById("metric-total-dispatched");
    const metricSent = document.getElementById("metric-sent-count");
    const metricSkipped = document.getElementById("metric-skipped-count");

    async function loadFeed() {
        const userId = parseInt(userIdInput.value || 1);
        try {
            const notifs = await fetchUserNotifications(userId, 30);

            if (!notifs || notifs.length === 0) {
                auditContainer.innerHTML = `
                    <div style="text-align: center; color: var(--text-muted); padding: 3rem;">
                        <p style="font-size: 1rem; font-weight: 700; margin-bottom: 0.35rem;">No notifications dispatched yet</p>
                        <p style="font-size: 0.85rem;">Use the dispatch console on the left to send your first message!</p>
                    </div>
                `;
                if (metricTotal) metricTotal.textContent = "0";
                if (metricSent) metricSent.textContent = "0";
                if (metricSkipped) metricSkipped.textContent = "0";
                return;
            }

            auditContainer.innerHTML = notifs.map(n => renderLogCard(n)).join("");

            if (metricTotal) metricTotal.textContent = notifs.length;
            if (metricSent) metricSent.textContent = notifs.filter(n => n.status === "Sent").length;
            if (metricSkipped) metricSkipped.textContent = notifs.filter(n => n.status === "Skipped").length;

        } catch {
            auditContainer.innerHTML = `
                <div style="text-align: center; color: var(--danger); padding: 2rem;">
                    Failed to connect to backend server. Make sure 'python run.py' is running.
                </div>
            `;
        }
    }

    refreshBtn?.addEventListener("click", loadFeed);

    // Initial Loads
    await loadTemplates();
    await loadUserPreferences(1);
    await loadFeed();

    // Auto poll feed every 3 seconds for live async status updates
    setInterval(loadFeed, 3000);
});
