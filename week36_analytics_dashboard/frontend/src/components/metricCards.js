import { formatNumber, formatPercent } from "../utils/helpers.js";

export function renderMetricCards(metrics = {}) {
    const container = document.getElementById("metric-cards-container");
    if (!container) return;

    const pageviews = metrics.pageviews || 0;
    const visitors = metrics.unique_visitors || 0;
    const avgViews = metrics.avg_views_per_session || 0;
    const bounceRate = metrics.bounce_rate_pct || 0;
    const deltas = metrics.growth_deltas || {};

    const viewsDelta = deltas.pageviews_delta_pct || 0;
    const visitorsDelta = deltas.visitors_delta_pct || 0;

    function getDeltaBadge(deltaVal) {
        if (deltaVal > 0) {
            return `<span class="delta-badge delta-positive">▲ ${formatPercent(deltaVal)}</span>`;
        } else if (deltaVal < 0) {
            return `<span class="delta-badge delta-negative">▼ ${formatPercent(deltaVal)}</span>`;
        }
        return `<span class="delta-badge delta-neutral">— 0.0%</span>`;
    }

    container.innerHTML = `
        <div class="metrics-grid">
            <!-- 1. Total Pageviews -->
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-label">Total Pageviews</span>
                    <div class="metric-icon-box">📈</div>
                </div>
                <div class="metric-value-row">
                    <span class="metric-number">${formatNumber(pageviews)}</span>
                    ${getDeltaBadge(viewsDelta)}
                </div>
                <span class="metric-subtitle">vs previous period</span>
            </div>

            <!-- 2. Unique Visitors -->
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-label">Unique Visitors</span>
                    <div class="metric-icon-box" style="color: var(--success); background-color: var(--success-bg);">👤</div>
                </div>
                <div class="metric-value-row">
                    <span class="metric-number">${formatNumber(visitors)}</span>
                    ${getDeltaBadge(visitorsDelta)}
                </div>
                <span class="metric-subtitle">distinct user sessions</span>
            </div>

            <!-- 3. Avg Views Per Session -->
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-label">Views / Session</span>
                    <div class="metric-icon-box" style="color: var(--info); background-color: rgba(59, 130, 246, 0.15);">📄</div>
                </div>
                <div class="metric-value-row">
                    <span class="metric-number">${avgViews}</span>
                </div>
                <span class="metric-subtitle">interaction depth</span>
            </div>

            <!-- 4. Bounce Rate -->
            <div class="metric-card">
                <div class="metric-card-top">
                    <span class="metric-label">Bounce Rate</span>
                    <div class="metric-icon-box" style="color: var(--warning); background-color: rgba(245, 158, 11, 0.15);">🚪</div>
                </div>
                <div class="metric-value-row">
                    <span class="metric-number">${bounceRate}%</span>
                </div>
                <span class="metric-subtitle">single-page visits</span>
            </div>
        </div>
    `;
}
