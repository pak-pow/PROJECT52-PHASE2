const API_BASE = "http://127.0.0.1:5000/api";

export async function apiFetchServices(category = "") {
    const url = category ? `${API_BASE}/services?category=${encodeURIComponent(category)}` : `${API_BASE}/services`;
    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to fetch services.");
    return data.services;
}

export async function apiFetchServiceDetail(serviceId) {
    const res = await fetch(`${API_BASE}/services/${serviceId}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to fetch service details.");
    return data;
}

export async function apiFetchProviders() {
    const res = await fetch(`${API_BASE}/providers`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to fetch providers.");
    return data.providers;
}

export async function apiFetchProviderAvailability(providerId, serviceId, dateStr) {
    const res = await fetch(`${API_BASE}/providers/${providerId}/availability?service_id=${serviceId}&date=${dateStr}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to fetch time slot availability.");
    return data;
}
