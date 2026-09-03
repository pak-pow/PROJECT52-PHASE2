import { renderNavbar } from "../components/navbar.js";
import { renderMetricCards } from "../components/metricCards.js";
import { renderTrafficChart, renderDeviceDonutChart, renderBrowserDonutChart } from "../components/charts.js";
import { renderTopPagesTable, renderBreakdownBars } from "../components/tables.js";
import { renderFunnelView } from "../components/funnelView.js";
import { renderLiveFeed } from "../components/liveFeed.js";
import { initTheme } from "../utils/theme.js";
import { showToast } from "../utils/helpers.js";
import {
    checkServerHealth,
    fetchOverview,
    fetchTimeseries,
    fetchBreakdowns,
    fetchTopPages,
    fetchFunnels,
    fetchFunnelMetrics,
    fetchLiveEvents,
    trackEvent,
    getExportCsvUrl
} from "../api/analyticsApi.js";

let currentStartDate = null;
let currentEndDate = null;
let currentInterval = "day";
let activeFunnelId = null;
let allFunnels = [];

document.addEventListener("DOMContentLoaded", async () => {
    initTheme();

    // 1. Initial Health Check
    const isOnline = await checkServerHealth();
    renderNavbar(isOnline);

    if (!isOnline) {
        showToast("Backend server offline. Run 'python run.py' on port 5000.", "warning");
    }

    // Default to 30 Days
    setDateRange("30d");

    // 2. Date Range Pill Buttons
    document.querySelectorAll(".date-pill-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".date-pill-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            const range = btn.getAttribute("data-range");
            setDateRange(range);
            loadDashboardData();
        });
    });

    function setDateRange(range) {
        const now = new Date();
        const formatDate = (d) => d.toISOString().split("T")[0];

        if (range === "today") {
            currentStartDate = formatDate(now);
            currentEndDate = formatDate(now);
            currentInterval = "hour";
        } else if (range === "7d") {
            const start = new Date();
            start.setDate(now.getDate() - 7);
            currentStartDate = formatDate(start);
            currentEndDate = formatDate(now);
            currentInterval = "day";
        } else if (range === "30d") {
            const start = new Date();
            start.setDate(now.getDate() - 30);
            currentStartDate = formatDate(start);
            currentEndDate = formatDate(now);
            currentInterval = "day";
        } else {
            currentStartDate = null;
            currentEndDate = null;
            currentInterval = "day";
        }
    }

    // 3. Funnel Selector Dropdown
    const funnelSelect = document.getElementById("select-funnel");
    async function loadFunnels() {
        try {
            const res = await fetchFunnels();
            allFunnels = res.funnels || [];
            if (funnelSelect) {
                funnelSelect.innerHTML = allFunnels.map(f => `
                    <option value="${f.id}">${f.name}</option>
                `).join("");
                if (allFunnels.length > 0) {
                    activeFunnelId = allFunnels[0].id;
                }
            }
        } catch {
            // Server offline fallback
        }
    }

    funnelSelect?.addEventListener("change", async (e) => {
        activeFunnelId = parseInt(e.target.value);
        await loadFunnelMetrics();
    });

    async function loadFunnelMetrics() {
        if (!activeFunnelId) return;
        try {
            const metrics = await fetchFunnelMetrics(activeFunnelId, currentStartDate, currentEndDate);
            renderFunnelView("funnel-view-container", metrics);
        } catch {
            // Ignore
        }
    }

    // 4. Main Dashboard Data Loader
    async function loadDashboardData() {
        try {
            // Load KPI Overview
            const overviewRes = await fetchOverview(currentStartDate, currentEndDate);
            renderMetricCards(overviewRes.metrics);

            // Load Timeseries Traffic
            const timeseriesRes = await fetchTimeseries(currentStartDate, currentEndDate, currentInterval);
            renderTrafficChart("trafficChartCanvas", timeseriesRes.data);

            // Load Breakdowns (Devices, Browsers, Referrers, Countries)
            const breakdownsRes = await fetchBreakdowns(currentStartDate, currentEndDate);
            renderDeviceDonutChart("deviceChartCanvas", breakdownsRes.devices);
            renderBrowserDonutChart("browserChartCanvas", breakdownsRes.browsers);
            renderBreakdownBars("referrers-container", breakdownsRes.referrers);
            renderBreakdownBars("countries-container", breakdownsRes.countries);

            // Load Top Pages Table
            const topPagesRes = await fetchTopPages(currentStartDate, currentEndDate, 8);
            renderTopPagesTable("top-pages-container", topPagesRes.pages);

            // Load Funnel Metrics
            await loadFunnelMetrics();
        } catch (err) {
            // Silent error during polling
        }
    }

    // 5. Live Stream Poller
    async function loadLiveFeed() {
        try {
            const res = await fetchLiveEvents(20);
            renderLiveFeed("live-feed-container", res.events);
            const liveCountEl = document.getElementById("live-events-count");
            if (liveCountEl) liveCountEl.textContent = res.count;
        } catch {
            // Ignore
        }
    }

    // 6. Quick Event Simulator
    document.getElementById("btn-simulate-event")?.addEventListener("click", async () => {
        const eventsList = ["pageview", "click", "signup", "purchase"];
        const randomEvent = eventsList[Math.floor(Math.random() * eventsList.length)];
        const paths = ["/pricing", "/docs", "/features", "/checkout", "/blog/scaling-apis"];
        const randomPath = paths[Math.floor(Math.random() * paths.length)];

        try {
            await trackEvent({
                event_name: randomEvent,
                session_id: `live_sim_${Math.floor(Math.random() * 9000 + 1000)}`,
                url_path: randomPath,
                country: "United States",
                metadata: { simulator: true }
            });
            showToast(`Dispatched event: ${randomEvent.toUpperCase()} on ${randomPath} ⚡`, "success");
            loadLiveFeed();
            loadDashboardData();
        } catch (err) {
            showToast("Failed to simulate event.", "error");
        }
    });

    // 7. Data Export Download Triggers
    document.getElementById("btn-export-csv")?.addEventListener("click", () => {
        const url = getExportCsvUrl(currentStartDate, currentEndDate, "traffic");
        window.open(url, "_blank");
    });

    document.getElementById("btn-export-events-csv")?.addEventListener("click", () => {
        const url = getExportCsvUrl(currentStartDate, currentEndDate, "events");
        window.open(url, "_blank");
    });

    document.getElementById("btn-refresh-data")?.addEventListener("click", () => {
        loadDashboardData();
        loadLiveFeed();
        showToast("Dashboard data refreshed! 🔄", "info");
    });

    // Initial Load
    await loadFunnels();
    await loadDashboardData();
    await loadLiveFeed();

    // Auto-poll live stream every 3.5 seconds
    setInterval(loadLiveFeed, 3500);
});
