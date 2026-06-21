export function renderDashboard(container) {
    container.innerHTML = `
        <div style="padding: 2rem;">
            <h1><i data-lucide="layout-dashboard"></i> Your Workspaces</h1>
            <p style="color: var(--text-muted); margin-top: 1rem;">The dashboard will go here.</p>
            <a href="#board/1" style="color: var(--accent); display: block; margin-top: 1rem;">Test Router: Go to Board 1 &rarr;</a>
        </div>
    `;
}