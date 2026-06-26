/**
 * api.js — Portfolio v2 API client
 * All fetch calls to the Flask backend go through here.
 */

const API_BASE = "http://localhost:5000/api";

// ── Helpers ────────────────────────────────────────────────────────────────

function getToken() {
    return localStorage.getItem("admin_token");
}

async function request(path, method = "GET", body = null, requiresAuth = false) {
    const headers = { "Content-Type": "application/json" };

    if (requiresAuth) {
        const token = getToken();
        if (token) headers["Authorization"] = `Bearer ${token}`;
    }

    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);

    const res = await fetch(`${API_BASE}${path}`, options);
    return res;
}

// ── Public API ─────────────────────────────────────────────────────────────

/** Fetch all portfolio projects (public) */
export async function getProjects() {
    const res = await request("/projects");
    if (!res.ok) throw new Error("Failed to load projects");
    return res.json();
}

/** Submit a contact form message (public) */
export async function submitContact(data) {
    const res = await request("/contact", "POST", data);
    const json = await res.json();
    if (!res.ok) throw new Error(json.error || "Submission failed");
    return json;
}

// ── Admin Auth ─────────────────────────────────────────────────────────────

/** Login as admin — returns token on success */
export async function adminLogin(username, password) {
    const res = await request("/admin/login", "POST", { username, password });
    const json = await res.json();
    if (!res.ok) throw new Error(json.error || "Invalid credentials");
    return json.token;
}

/** Logout (invalidates current token) */
export async function adminLogout() {
    await request("/admin/logout", "POST", null, true);
    localStorage.removeItem("admin_token");
}

// ── Admin Messages ─────────────────────────────────────────────────────────

/** Get all contact messages */
export async function getMessages() {
    const res = await request("/admin/messages", "GET", null, true);
    if (!res.ok) throw new Error("Failed to load messages");
    return res.json();
}

/** Toggle read/unread on a message */
export async function toggleRead(id) {
    const res = await request(`/admin/messages/${id}/read`, "PATCH", null, true);
    if (!res.ok) throw new Error("Failed to update message");
    return res.json();
}

/** Permanently delete a message */
export async function deleteMessage(id) {
    const res = await request(`/admin/messages/${id}`, "DELETE", null, true);
    if (!res.ok) throw new Error("Failed to delete message");
}

// ── Admin Projects ─────────────────────────────────────────────────────────

/** Create a new project */
export async function createProject(data) {
    const res = await request("/projects", "POST", data, true);
    const json = await res.json();
    if (!res.ok) throw new Error(json.error || "Failed to create project");
    return json;
}

/** Update an existing project */
export async function updateProject(id, data) {
    const res = await request(`/projects/${id}`, "PUT", data, true);
    const json = await res.json();
    if (!res.ok) throw new Error(json.error || "Failed to update project");
    return json;
}

/** Delete a project */
export async function deleteProject(id) {
    const res = await request(`/projects/${id}`, "DELETE", null, true);
    if (!res.ok) throw new Error("Failed to delete project");
}
