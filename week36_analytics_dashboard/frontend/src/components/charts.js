let trafficChartInstance = null;
let deviceChartInstance = null;
let browserChartInstance = null;

export function renderTrafficChart(canvasId, timeseriesData = []) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === "undefined") return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    if (trafficChartInstance) {
        trafficChartInstance.destroy();
    }

    const labels = timeseriesData.map(d => d.bucket);
    const pageviews = timeseriesData.map(d => d.pageviews);
    const uniqueVisitors = timeseriesData.map(d => d.unique_visitors);

    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const gridColor = isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)";
    const textColor = isDark ? "#94a3b8" : "#64748b";

    // Gradient background for pageviews
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, "rgba(99, 102, 241, 0.35)");
    gradient.addColorStop(1, "rgba(99, 102, 241, 0.0)");

    trafficChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Pageviews",
                    data: pageviews,
                    borderColor: "#6366f1",
                    backgroundColor: gradient,
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.35,
                    pointRadius: timeseriesData.length > 30 ? 0 : 3,
                    pointHoverRadius: 6,
                    pointBackgroundColor: "#6366f1"
                },
                {
                    label: "Unique Visitors",
                    data: uniqueVisitors,
                    borderColor: "#10b981",
                    backgroundColor: "transparent",
                    borderWidth: 2,
                    borderDash: [4, 4],
                    tension: 0.35,
                    pointRadius: timeseriesData.length > 30 ? 0 : 3,
                    pointHoverRadius: 6,
                    pointBackgroundColor: "#10b981"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false
            },
            plugins: {
                legend: {
                    position: "top",
                    labels: { color: textColor, font: { weight: "600" } }
                },
                tooltip: {
                    backgroundColor: isDark ? "#1e293b" : "#ffffff",
                    titleColor: isDark ? "#f8fafc" : "#0f172a",
                    bodyColor: isDark ? "#cbd5e1" : "#334155",
                    borderColor: isDark ? "#334155" : "#e2e8f0",
                    borderWidth: 1,
                    padding: 10,
                    boxPadding: 4
                }
            },
            scales: {
                x: {
                    grid: { color: gridColor },
                    ticks: { color: textColor, maxTicksLimit: 12 }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: gridColor },
                    ticks: { color: textColor }
                }
            }
        }
    });
}

export function renderDeviceDonutChart(canvasId, devicesList = []) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === "undefined") return;

    if (deviceChartInstance) {
        deviceChartInstance.destroy();
    }

    const labels = devicesList.map(d => d.label.charAt(0).toUpperCase() + d.label.slice(1));
    const data = devicesList.map(d => d.count);
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const textColor = isDark ? "#94a3b8" : "#64748b";

    const colors = ["#6366f1", "#10b981", "#f59e0b", "#3b82f6", "#ec4899"];

    deviceChartInstance = new Chart(canvas.getContext("2d"), {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "right",
                    labels: { color: textColor, font: { size: 11, weight: "600" } }
                }
            },
            cutout: "68%"
        }
    });
}

export function renderBrowserDonutChart(canvasId, browsersList = []) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === "undefined") return;

    if (browserChartInstance) {
        browserChartInstance.destroy();
    }

    const labels = browsersList.map(b => b.label);
    const data = browsersList.map(b => b.count);
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const textColor = isDark ? "#94a3b8" : "#64748b";

    const colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444", "#64748b"];

    browserChartInstance = new Chart(canvas.getContext("2d"), {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "right",
                    labels: { color: textColor, font: { size: 11, weight: "600" } }
                }
            },
            cutout: "68%"
        }
    });
}
