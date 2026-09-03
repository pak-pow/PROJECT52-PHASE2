import { escapeHtml, formatTimestamp } from "../utils/helpers.js";

export function renderLiveFeed(containerId, events = []) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!events || events.length === 0) {
        container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem; text-align: center; padding: 2rem;">Waiting for incoming telemetry events...</p>`;
        return;
    }

    function getEventBadge(name) {
        let bg = "rgba(99, 102, 241, 0.15)";
        let color = "#6366f1";
        let icon = "⚡";

        if (name === "pageview") { bg = "rgba(59, 130, 246, 0.15)"; color = "#3b82f6"; icon = "📄"; }
        if (name === "click") { bg = "rgba(100, 116, 139, 0.15)"; color = "#64748b"; icon = "🖱️"; }
        if (name === "signup") { bg = "rgba(16, 185, 129, 0.15)"; color = "#10b981"; icon = "👤"; }
        if (name === "purchase") { bg = "rgba(245, 158, 11, 0.15)"; color = "#f59e0b"; icon = "💰"; }

        return `<span style="background: ${bg}; color: ${color}; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase;">${icon} ${escapeHtml(name)}</span>`;
    }

    container.innerHTML = events.slice(0, 25).map(e => `
        <div style="background: var(--bg-base); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 0.65rem 0.85rem; display: flex; flex-direction: column; gap: 0.35rem; transition: border-color 0.2s;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 0.4rem;">
                    ${getEventBadge(e.event_name)}
                    <span style="font-family: var(--font-mono); font-size: 0.82rem; font-weight: 600; color: var(--text-primary);">${escapeHtml(e.url_path)}</span>
                </div>
                <span style="font-size: 0.72rem; color: var(--text-muted);">${formatTimestamp(e.created_at)}</span>
            </div>

            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted);">
                <span>💻 ${escapeHtml(e.browser || "Chrome")} on ${escapeHtml(e.os || "Windows")} (${escapeHtml(e.device_type || "desktop")})</span>
                <span>🌍 ${escapeHtml(e.country || "United States")}</span>
            </div>
        </div>
    `).join("");
}
