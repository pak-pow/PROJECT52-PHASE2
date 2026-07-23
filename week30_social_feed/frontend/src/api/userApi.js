/**
 * userApi.js — User/profile API client (profile, posts, follow, update).
 */
import { API_BASE, fetchAuth } from "./authApi.js";

export async function apiGetProfile(username) {
    const resp = await fetchAuth(`${API_BASE}/users/${username}`);
    return { ok: resp.ok, data: await resp.json() };
}

export async function apiGetUserPosts(username, beforeId = null) {
    const qs = beforeId ? `?before=${beforeId}` : "";
    const resp = await fetchAuth(`${API_BASE}/users/${username}/posts${qs}`);
    return resp.ok ? await resp.json() : [];
}

export async function apiToggleFollow(username) {
    const resp = await fetchAuth(`${API_BASE}/users/${username}/follow`, { method: "POST" });
    return { ok: resp.ok, data: await resp.json() };
}

export async function apiGetFollowers(username) {
    const resp = await fetchAuth(`${API_BASE}/users/${username}/followers`);
    return resp.ok ? await resp.json() : [];
}

export async function apiGetFollowing(username) {
    const resp = await fetchAuth(`${API_BASE}/users/${username}/following`);
    return resp.ok ? await resp.json() : [];
}

export function avatarUrl(username) {
    return `${API_BASE}/users/${username}/avatar`;
}

export async function apiGetSuggestions() {
    const resp = await fetchAuth(`${API_BASE}/users/suggestions`);
    return resp.ok ? await resp.json() : [];
}

export async function apiUpdateProfile({ displayName, bio, avatarFile } = {}) {
    const form = new FormData();
    if (displayName !== undefined) form.append("display_name", displayName);
    if (bio         !== undefined) form.append("bio",          bio);
    if (avatarFile)                form.append("avatar",       avatarFile);
    const resp = await fetchAuth(`${API_BASE}/users/me`, { method: "PUT", body: form });
    return { ok: resp.ok, data: await resp.json() };
}

export async function apiSearchUsers(q) {
    const resp = await fetchAuth(`${API_BASE}/users/search?q=${encodeURIComponent(q)}`);
    return resp.ok ? await resp.json() : [];
}
