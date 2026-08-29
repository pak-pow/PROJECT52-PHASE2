const API_BASE_URL = "http://127.0.0.1:5000/api";

export async function checkServerHealth() {
    try {
        const res = await fetch(`${API_BASE_URL}/health`);
        return res.ok;
    } catch {
        return false;
    }
}

export async function sendNotification(payload) {
    const res = await fetch(`${API_BASE_URL}/notifications/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok && res.status !== 200 && res.status !== 202) {
        throw new Error(data.error || "Failed to enqueue notification.");
    }
    return data;
}

export async function fetchNotificationById(id) {
    const res = await fetch(`${API_BASE_URL}/notifications/${id}`);
    if (!res.ok) throw new Error("Notification record not found.");
    return await res.json();
}

export async function fetchUserNotifications(userId, limit = 20) {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/notifications?limit=${limit}`);
    if (!res.ok) throw new Error("Failed to fetch notification history.");
    return await res.json();
}

export async function fetchTemplates() {
    const res = await fetch(`${API_BASE_URL}/templates`);
    if (!res.ok) throw new Error("Failed to fetch templates.");
    return await res.json();
}

export async function fetchUserPreferences(userId) {
    const res = await fetch(`${API_BASE_URL}/preferences/${userId}`);
    if (!res.ok) throw new Error("Failed to fetch user preferences.");
    return await res.json();
}

export async function updateUserPreferences(userId, prefs) {
    const res = await fetch(`${API_BASE_URL}/preferences/${userId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(prefs)
    });
    if (!res.ok) throw new Error("Failed to update preferences.");
    return await res.json();
}
