/**
 * authApi.js — Authentication API client (register, login, logout, me).
 * Uses Bearer token stored in localStorage under "sf_token".
 */

import { showToast } from "../utils/helpers.js";

export const API_BASE = "http://127.0.0.1:5000/api";

const SESSION_TTL_MS = 30 * 60 * 1000; // 30 minutes

function setStorage(key, val) {
    sessionStorage.setItem(key, val);
}

function getStorage(key) {
    return sessionStorage.getItem(key) || localStorage.getItem(key) || "";
}

export function saveSession(token, username, displayName, avatarPath) {
    const expiresAt = Date.now() + SESSION_TTL_MS;
    sessionStorage.setItem("sf_token", token);
    sessionStorage.setItem("sf_username", username);
    sessionStorage.setItem("sf_display_name", displayName || username);
    sessionStorage.setItem("sf_avatar_path", avatarPath || "");
    sessionStorage.setItem("sf_expires_at", String(expiresAt));
}

export function extendSession() {
    const expiresAt = Date.now() + SESSION_TTL_MS;
    if (sessionStorage.getItem("sf_token")) {
        sessionStorage.setItem("sf_expires_at", String(expiresAt));
    }
}

export function clearSession() {
    ["sf_token", "sf_username", "sf_display_name", "sf_avatar_path", "sf_expires_at"].forEach(k => {
        sessionStorage.removeItem(k);
        localStorage.removeItem(k);
    });
}

export function getToken() {
    const expiresAt = parseInt(getStorage("sf_expires_at"), 10);
    if (expiresAt && Date.now() > expiresAt) {
        clearSession();
        return "";
    }
    return getStorage("sf_token");
}

export function getSessionUser() {
    const token = getToken();
    if (!token) return null;
    return {
        token,
        username: getStorage("sf_username"),
        displayName: getStorage("sf_display_name"),
        avatarPath: getStorage("sf_avatar_path"),
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
            if (!window.location.pathname.endsWith("login.html") && !window.location.pathname.endsWith("register.html")) {
                window.location.href = "login.html";
            }
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
