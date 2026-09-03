import { escapeHtml, formatNumber } from "../utils/helpers.js";

export function renderTopPagesTable(containerId, pages = []) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!pages || pages.length === 0) {
        container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem; text-align: center; padding: 2rem;">No page views recorded in this period.</p>`;
        return;
    }

    const rowsHtml = pages.map((p, idx) => `
        <tr style="border-bottom: 1px solid var(--border); transition: background 0.15s;">
            <td style="padding: 0.75rem 0.5rem; font-weight: 700; font-size: 0.85rem; color: var(--text-muted);">#${idx + 1}</td>
            <td style="padding: 0.75rem 0.5rem; font-family: var(--font-mono); font-size: 0.85rem; color: var(--accent-light);">
                ${escapeHtml(p.url_path)}
            </td>
            <td style="padding: 0.75rem 0.5rem; text-align: right; font-weight: 700; font-size: 0.88rem;">
                ${formatNumber(p.views)}
            </td>
            <td style="padding: 0.75rem 0.5rem; text-align: right; font-size: 0.85rem; color: var(--text-secondary);">
                ${formatNumber(p.unique_visitors)}
            </td>
            <td style="padding: 0.75rem 0.5rem; width: 120px;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="flex: 1; height: 6px; background: var(--bg-input); border-radius: 4px; overflow: hidden;">
                        <div style="width: ${p.share_pct}%; height: 100%; background: var(--accent); border-radius: 4px;"></div>
                    </div>
                    <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-muted); width: 35px; text-align: right;">${p.share_pct}%</span>
                </div>
            </td>
        </tr>
    `).join("");

    container.innerHTML = `
        <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
                <tr style="border-bottom: 2px solid var(--border); color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase;">
                    <th style="padding: 0.5rem;">Rank</th>
                    <th style="padding: 0.5rem;">URL Path</th>
                    <th style="padding: 0.5rem; text-align: right;">Views</th>
                    <th style="padding: 0.5rem; text-align: right;">Visitors</th>
                    <th style="padding: 0.5rem;">Share</th>
                </tr>
            </thead>
            <tbody>
                ${rowsHtml}
            </tbody>
        </table>
    `;
}

export function renderBreakdownBars(containerId, items = []) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!items || items.length === 0) {
        container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem; text-align: center; padding: 1.5rem;">No data available.</p>`;
        return;
    }

    container.innerHTML = items.slice(0, 5).map(item => `
        <div class="breakdown-row">
            <div class="breakdown-info">
                <span>${escapeHtml(item.label)}</span>
                <span style="color: var(--text-muted); font-size: 0.8rem;">
                    <strong>${formatNumber(item.count)}</strong> (${item.percentage}%)
                </span>
            </div>
            <div class="breakdown-progress-track">
                <div class="breakdown-progress-fill" style="width: ${item.percentage}%;"></div>
            </div>
        </div>
    `).join("");
}
