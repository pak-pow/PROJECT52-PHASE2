import { getToken, saveSession, clearSession } from "../utils/authCheck.js";

const API_BASE = "http://127.0.0.1:5000/api";

export async function apiRegister(username, display_name, email, password) {
    const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, display_name, email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Registration failed.");
    saveSession(data.token, data.user);
    return data;
}

export async function apiLogin(username, password) {
    const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Login failed.");
    saveSession(data.token, data.user);
    return data;
}

export async function apiLogout() {
    const token = getToken();
    if (token) {
        try {
            await fetch(`${API_BASE}/auth/logout`, {
                method: "POST",
                headers: { "Authorization": `Bearer ${token}` }
            });
        } catch {
            // Ignore fetch errors during logout cleanup
        }
    }
    clearSession();
}
