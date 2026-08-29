import { escapeHtml, formatTimestamp } from "../utils/helpers.js";

export function renderLogCard(notif) {
    let channelClass = "badge-email";
    if (notif.channel === "sms") channelClass = "badge-sms";
    if (notif.channel === "webhook") channelClass = "badge-webhook";

    let statusClass = "badge-queued";
    if (notif.status === "Sent") statusClass = "badge-sent";
    if (notif.status === "Processing") statusClass = "badge-processing";
    if (notif.status === "Skipped") statusClass = "badge-skipped";
    if (notif.status === "Failed") statusClass = "badge-failed";

    return `
        <div class="log-item-card" data-id="${notif.id}">
            <div class="log-header-row">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span class="channel-badge ${channelClass}">${escapeHtml(notif.channel)}</span>
                    <span style="font-weight: 700; font-size: 0.9rem;">#${notif.id}</span>
                    <span style="font-size: 0.82rem; color: var(--text-secondary);">→ ${escapeHtml(notif.recipient)}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span class="status-badge ${statusClass}">${escapeHtml(notif.status)}</span>
                </div>
            </div>

            ${notif.subject ? `<div style="font-weight: 600; font-size: 0.85rem; color: var(--accent-light);">📧 ${escapeHtml(notif.subject)}</div>` : ''}

            <div class="log-content-box">${escapeHtml(notif.content)}</div>

            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: var(--text-muted);">
                <span>📅 ${formatTimestamp(notif.created_at)}</span>
                <span>Attempts: <strong>${notif.attempts || 0}</strong> ${notif.error_message ? `• <span style="color: var(--danger);">${escapeHtml(notif.error_message)}</span>` : ''}</span>
            </div>
        </div>
    `;
}
