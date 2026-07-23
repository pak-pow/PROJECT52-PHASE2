/**
 * authApi.js — Authentication API client (register, login, logout, me).
 * Uses Bearer token stored in localStorage under "sf_token".
 */

import { showToast } from "../utils/helpers.js";

export const API_BASE = "http://localhost:5000/api";

// ── Local storage helpers ────────────────────────────────────
export function saveSession(token, username, displayName, avatarPath) {
    localStorage.setItem("sf_token", token);
    localStorage.setItem("sf_username", username);
    localStorage.setItem("sf_display_name", displayName || username);
    localStorage.setItem("sf_avatar_path", avatarPath || "");
}

export function clearSession() {
    ["sf_token", "sf_username", "sf_display_name", "sf_avatar_path"].forEach(k =>
        localStorage.removeItem(k)
    );
}

export function getToken() {
    return localStorage.getItem("sf_token") || "";
}

export function getSessionUser() {
    const token = getToken();
    if (!token) return null;
    return {
        token,
        username: localStorage.getItem("sf_username") || "",
        displayName: localStorage.getItem("sf_display_name") || "",
        avatarPath: localStorage.getItem("sf_avatar_path") || "",
    };
}

export function authHeaders() {
    return { Authorization: `Bearer ${getToken()}` };
}

export async function fetchAuth(url, options = {}) {
    const headers = { ...authHeaders(), ...(options.headers || {}) };
    try {
        const resp = await fetch(url, { ...options, headers });
        if (resp.status === 401) {
            clearSession();
            window.location.href = "login.html";
        }
        return resp;
    } catch (err) {
        showToast("Cannot connect to backend server. Is run.py running?", "error");
        return {
            ok: false,
            status: 503,
            json: async () => ({ error: "Backend server offline" }),
        };
    }
}

// ── Auth API calls ───────────────────────────────────────────
export async function apiRegister(username, displayName, password) {
    const resp = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, display_name: displayName, password }),
    });
    return { ok: resp.ok, data: await resp.json() };
}

export async function apiLogin(username, password) {
    const resp = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    return { ok: resp.ok, data: await resp.json() };
}

export async function apiLogout() {
    await fetchAuth(`${API_BASE}/auth/logout`, { method: "POST" });
    clearSession();
}

export async function apiMe() {
    const resp = await fetchAuth(`${API_BASE}/auth/me`);
    return { ok: resp.ok, data: await resp.json() };
}
