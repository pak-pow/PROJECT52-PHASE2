import { escapeHtml, formatNumber } from "../utils/helpers.js";

export function renderFunnelView(containerId, metrics = null) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!metrics || !metrics.steps_analysis || metrics.steps_analysis.length === 0) {
        container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem; text-align: center; padding: 2rem;">No conversion data available for this funnel.</p>`;
        return;
    }

    const stepsHtml = metrics.steps_analysis.map((step, idx) => {
        const isFirst = idx === 0;
        return `
            <div style="display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: baseline; font-size: 0.85rem;">
                    <div>
                        <strong style="color: var(--text-primary);">${step.step_order}. ${escapeHtml(step.step_name)}</strong>
                        <span style="font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-mono); margin-left: 0.4rem;">(${escapeHtml(step.event_name)})</span>
                    </div>
                    <div style="font-weight: 700; font-size: 0.9rem;">
                        ${formatNumber(step.visitors_reached)} <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-muted);">visitors</span>
                    </div>
                </div>

                <div style="width: 100%; height: 26px; background-color: var(--bg-input); border-radius: var(--radius-sm); overflow: hidden; display: flex; align-items: center; position: relative;">
                    <div style="width: ${step.overall_conversion_pct}%; height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent-light)); border-radius: var(--radius-sm); transition: width 0.5s ease;"></div>
                    <span style="position: absolute; right: 8px; font-size: 0.75rem; font-weight: 700; color: var(--text-primary);">
                        ${step.overall_conversion_pct}% of total
                    </span>
                </div>

                ${!isFirst ? `
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); padding: 0 0.2rem;">
                        <span>Step Conversion: <strong style="color: var(--success);">${step.step_conversion_pct}%</strong></span>
                        <span>Drop-off: <strong style="color: var(--danger);">${step.drop_off_pct}%</strong> (-${formatNumber(step.drop_off_count)})</span>
                    </div>
                ` : ''}
            </div>
        `;
    }).join("");

    container.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-input); padding: 0.75rem 1rem; border-radius: var(--radius-md); margin-bottom: 1.25rem;">
            <div>
                <span style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Overall Conversion</span>
                <div style="font-size: 1.35rem; font-weight: 800; color: var(--success);">${metrics.overall_conversion_pct}%</div>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Converted Sessions</span>
                <div style="font-size: 1.35rem; font-weight: 800;">${formatNumber(metrics.final_conversions)} / ${formatNumber(metrics.initial_visitors)}</div>
            </div>
        </div>

        <div>
            ${stepsHtml}
        </div>
    `;
}
