const API_BASE_URL = "http://127.0.0.1:5000/api";

function buildQueryString(params = {}) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
        if (val !== undefined && val !== null && val !== "") {
            searchParams.append(key, val);
        }
    });
    const qs = searchParams.toString();
    return qs ? `?${qs}` : "";
}

export async function checkServerHealth() {
    try {
        const res = await fetch(`${API_BASE_URL}/health`);
        return res.ok;
    } catch {
        return false;
    }
}

export async function fetchOverview(startDate, endDate) {
    const qs = buildQueryString({ start_date: startDate, end_date: endDate });
    const res = await fetch(`${API_BASE_URL}/analytics/overview${qs}`);
    if (!res.ok) throw new Error("Failed to fetch overview metrics.");
    return await res.json();
}

export async function fetchTimeseries(startDate, endDate, interval = "day") {
    const qs = buildQueryString({ start_date: startDate, end_date: endDate, interval });
    const res = await fetch(`${API_BASE_URL}/analytics/timeseries${qs}`);
    if (!res.ok) throw new Error("Failed to fetch timeseries traffic.");
    return await res.json();
}

export async function fetchBreakdowns(startDate, endDate) {
    const qs = buildQueryString({ start_date: startDate, end_date: endDate });
    const res = await fetch(`${API_BASE_URL}/analytics/breakdown${qs}`);
    if (!res.ok) throw new Error("Failed to fetch breakdown distributions.");
    return await res.json();
}

export async function fetchTopPages(startDate, endDate, limit = 10) {
    const qs = buildQueryString({ start_date: startDate, end_date: endDate, limit });
    const res = await fetch(`${API_BASE_URL}/analytics/top-pages${qs}`);
    if (!res.ok) throw new Error("Failed to fetch top pages.");
    return await res.json();
}

export async function fetchFunnels() {
    const res = await fetch(`${API_BASE_URL}/funnels`);
    if (!res.ok) throw new Error("Failed to fetch funnels list.");
    return await res.json();
}

export async function fetchFunnelMetrics(funnelId, startDate, endDate) {
    const qs = buildQueryString({ start_date: startDate, end_date: endDate });
    const res = await fetch(`${API_BASE_URL}/funnels/${funnelId}/metrics${qs}`);
    if (!res.ok) throw new Error("Failed to fetch funnel conversion metrics.");
    return await res.json();
}

export async function fetchLiveEvents(limit = 30) {
    const res = await fetch(`${API_BASE_URL}/events/live?limit=${limit}`);
    if (!res.ok) throw new Error("Failed to fetch live event stream.");
    return await res.json();
}

export async function trackEvent(payload) {
    const res = await fetch(`${API_BASE_URL}/events`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("Failed to ingest event.");
    return await res.json();
}

export function getExportCsvUrl(startDate, endDate, type = "traffic") {
    const qs = buildQueryString({ start_date: startDate, end_date: endDate, type });
    return `${API_BASE_URL}/export/csv${qs}`;
}
