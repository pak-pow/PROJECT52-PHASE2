/**
 * postApi.js — Post API client (feed, explore, create, delete, like).
 */
import { API_BASE, fetchAuth } from "./authApi.js";

export async function apiFeed(beforeId = null) {
    const qs = beforeId ? `?before=${beforeId}` : "";
    const resp = await fetchAuth(`${API_BASE}/posts${qs}`);
    return resp.ok ? await resp.json() : [];
}

export async function apiExplore(beforeId = null, tag = null) {
    let url = `${API_BASE}/posts/explore`;
    const params = new URLSearchParams();
    if (beforeId) params.set("before", beforeId);
    if (tag)      params.set("tag",    tag);
    if ([...params].length) url += "?" + params.toString();
    const resp = await fetchAuth(url);
    return resp.ok ? await resp.json() : [];
}

export async function apiGetPost(postId) {
    const resp = await fetchAuth(`${API_BASE}/posts/${postId}`);
    return { ok: resp.ok, data: await resp.json() };
}

export async function apiCreatePost(content, imageFile = null, replyToId = null, repostOfId = null) {
    const form = new FormData();
    form.append("content", content);
    if (imageFile) form.append("image", imageFile);
    if (replyToId) form.append("reply_to_id", replyToId);
    if (repostOfId) form.append("repost_of_id", repostOfId);

    const resp = await fetchAuth(`${API_BASE}/posts`, { method: "POST", body: form });
    return { ok: resp.ok, data: await resp.json() };
}

export async function apiDeletePost(postId) {
    const resp = await fetchAuth(`${API_BASE}/posts/${postId}`, { method: "DELETE" });
    return { ok: resp.ok };
}

export async function apiLikePost(postId) {
    const resp = await fetchAuth(`${API_BASE}/posts/${postId}/like`, { method: "POST" });
    return { ok: resp.ok, data: await resp.json() };
}

export async function apiRepostPost(postId) {
    const resp = await fetchAuth(`${API_BASE}/posts/${postId}/repost`, { method: "POST" });
    return { ok: resp.ok, data: await resp.json() };
}

export function postImageUrl(postId) {
    return `${API_BASE}/posts/${postId}/image`;
}
