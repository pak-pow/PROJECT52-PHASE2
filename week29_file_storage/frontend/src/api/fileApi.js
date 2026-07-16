/* ═══════════════════════════════════════════════════════════════
   FileVault — API Client
   ═══════════════════════════════════════════════════════════════ */

const API_BASE = "http://localhost:5000/api";

/** Get the stored auth token. */
function getToken() {
    return localStorage.getItem("fv_token");
}

/** Build Authorization headers. */
function authHeaders() {
    const token = getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
}


// ── Auth ──────────────────────────────────────────────────────

export async function register(username, password) {
    const resp = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    return resp.json().then((data) => ({ ok: resp.ok, status: resp.status, data }));
}

export async function login(username, password) {
    const resp = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    return resp.json().then((data) => ({ ok: resp.ok, status: resp.status, data }));
}

export async function logout() {
    await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        headers: { ...authHeaders() },
    });
    localStorage.removeItem("fv_token");
    localStorage.removeItem("fv_user");
}


// ── Files ─────────────────────────────────────────────────────

/**
 * Upload files with XHR to track per-request progress.
 * @param {FileList|File[]} files
 * @param {function} onProgress  - (percent: number) => void
 * @returns {Promise<object>}
 */
export function uploadFiles(files, onProgress) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        const formData = new FormData();
        for (const f of files) formData.append("files", f);

        xhr.upload.addEventListener("progress", (e) => {
            if (e.lengthComputable && onProgress) {
                onProgress(Math.round((e.loaded / e.total) * 100));
            }
        });

        xhr.addEventListener("load", () => {
            try {
                const data = JSON.parse(xhr.responseText);
                resolve({ ok: xhr.status >= 200 && xhr.status < 300, status: xhr.status, data });
            } catch {
                reject(new Error("Invalid server response."));
            }
        });

        xhr.addEventListener("error", () => reject(new Error("Upload failed.")));

        xhr.open("POST", `${API_BASE}/files/upload`);
        const token = getToken();
        if (token) xhr.setRequestHeader("Authorization", `Bearer ${token}`);
        xhr.send(formData);
    });
}

async function fetchWithAuth(url, options = {}) {
    const headers = {
        ...authHeaders(),
        ...(options.headers || {}),
    };
    const resp = await fetch(url, { ...options, headers });
    if (resp.status === 401) {
        localStorage.removeItem("fv_token");
        localStorage.removeItem("fv_user");
        window.location.reload();
        throw new Error("Session expired.");
    }
    return resp;
}

export async function listFiles(category) {
    const qs = category && category !== "all" ? `?category=${category}` : "";
    const resp = await fetchWithAuth(`${API_BASE}/files${qs}`);
    return resp.json();
}

export async function getFile(id) {
    const resp = await fetchWithAuth(`${API_BASE}/files/${id}`);
    return resp.json();
}

export function downloadUrl(id) {
    return `${API_BASE}/files/${id}/download`;
}

export function thumbnailUrl(id) {
    return `${API_BASE}/files/${id}/thumbnail`;
}

export async function deleteFile(id) {
    const resp = await fetchWithAuth(`${API_BASE}/files/${id}`, {
        method: "DELETE",
    });
    return { ok: resp.ok, data: await resp.json() };
}

export async function renameFile(id, originalName) {
    const resp = await fetchWithAuth(`${API_BASE}/files/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ original_name: originalName }),
    });
    return { ok: resp.ok, data: await resp.json() };
}
