/* ═══════════════════════════════════════════════════════════════
   Preview Modal Component
   ═══════════════════════════════════════════════════════════════ */

import { thumbnailUrl, downloadUrl, deleteFile } from "../api/fileApi.js";
import { formatBytes, formatDate, getFileIcon } from "../utils/helpers.js";

const overlay = () => document.getElementById("preview-modal");
const body = () => document.getElementById("modal-body");

// Keep track of object URLs to prevent memory leaks
let activeObjectUrls = [];

export function initPreviewModal() {
    const modal = overlay();
    // Close on backdrop click
    modal.addEventListener("click", (e) => {
        if (e.target === modal) closePreview();
    });
    // Close button
    modal.querySelector(".modal-close").addEventListener("click", closePreview);
    // Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closePreview();
    });
}

export function openPreview(file) {
    const modal = overlay();
    const content = body();
    const token = localStorage.getItem("fv_token");

    const ext = file.original_name.split(".").pop().toLowerCase();
    const isImage = file.category === "image";
    const isAudio = file.category === "audio";
    const isVideo = file.category === "video";
    const isText = ["txt", "md", "csv", "json", "js", "py", "html", "css"].includes(ext);

    // Build the dynamic preview placeholder
    let previewElHtml = "";
    if (isImage) {
        previewElHtml = `<img src="${thumbnailUrl(file.id)}" alt="${escapeHtml(file.original_name)}" id="modal-img-preview" />`;
    } else if (isAudio) {
        previewElHtml = `<audio controls id="modal-audio-preview" class="media-player"></audio>`;
    } else if (isVideo) {
        previewElHtml = `<video controls id="modal-video-preview" class="media-player"></video>`;
    } else if (isText) {
        previewElHtml = `<pre class="modal-text-preview"><code id="modal-text-code">Loading content…</code></pre>`;
    } else {
        previewElHtml = `<span class="no-preview-icon">${getFileIcon(file.original_name, file.category)}</span>`;
    }

    content.innerHTML = `
        <div class="modal-preview">
            ${previewElHtml}
        </div>
        <div class="modal-details">
            <h3 class="modal-filename">${escapeHtml(file.original_name)}</h3>
            <div class="modal-meta-grid">
                <span class="modal-meta-label">Type</span>
                <span class="modal-meta-value">${file.mime_type}</span>
                <span class="modal-meta-label">Size</span>
                <span class="modal-meta-value">${formatBytes(file.file_size)}</span>
                <span class="modal-meta-label">Category</span>
                <span class="modal-meta-value" style="text-transform:capitalize">${file.category}</span>
                <span class="modal-meta-label">Uploaded</span>
                <span class="modal-meta-value">${formatDate(file.uploaded_at)}</span>
            </div>
            <div class="modal-actions">
                <a href="${downloadUrl(file.id)}" class="btn btn-primary" id="modal-download-btn">⬇ Download</a>
                <button class="btn btn-danger" id="modal-delete-btn">🗑 Delete</button>
            </div>
        </div>
    `;

    // Fetch and bind auth-protected file data
    if (isImage) {
        const img = content.querySelector("#modal-img-preview");
        fetchBlobUrl(downloadUrl(file.id), token).then(url => {
            if (url) img.src = url;
        });
    } else if (isAudio) {
        const audio = content.querySelector("#modal-audio-preview");
        fetchBlobUrl(downloadUrl(file.id), token).then(url => {
            if (url) audio.src = url;
        });
    } else if (isVideo) {
        const video = content.querySelector("#modal-video-preview");
        fetchBlobUrl(downloadUrl(file.id), token).then(url => {
            if (url) video.src = url;
        });
    } else if (isText) {
        const code = content.querySelector("#modal-text-code");
        fetch(downloadUrl(file.id), {
            headers: { Authorization: `Bearer ${token}` }
        })
        .then(r => r.text())
        .then(txt => { code.textContent = txt; })
        .catch(() => { code.textContent = "Failed to load content preview."; });
    }

    // Attach auth header to download link
    const dlBtn = content.querySelector("#modal-download-btn");
    dlBtn.addEventListener("click", async (e) => {
        e.preventDefault();
        const url = await fetchBlobUrl(downloadUrl(file.id), token, false);
        if (url) {
            const a = document.createElement("a");
            a.href = url;
            a.download = file.original_name;
            a.click();
        }
    });

    // Hook up delete button
    const delBtn = content.querySelector("#modal-delete-btn");
    delBtn.addEventListener("click", async () => {
        if (!confirm(`Delete "${file.original_name}"?`)) return;
        const result = await deleteFile(file.id);
        if (result.ok) {
            closePreview();
            document.dispatchEvent(new CustomEvent("file-deleted"));
        }
    });

    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
}

async function fetchBlobUrl(url, token, autoRevokeOnClose = true) {
    try {
        const resp = await fetch(url, {
            headers: { Authorization: `Bearer ${token}` }
        });
        const blob = await resp.blob();
        const blobUrl = URL.createObjectURL(blob);
        if (autoRevokeOnClose) activeObjectUrls.push(blobUrl);
        return blobUrl;
    } catch {
        return null;
    }
}

export function closePreview() {
    const modal = overlay();
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");

    // Stop and clean up any media players
    const audio = modal.querySelector("audio");
    if (audio) audio.pause();
    const video = modal.querySelector("video");
    if (video) video.pause();

    // Revoke object URLs to prevent leaks
    activeObjectUrls.forEach(url => URL.revokeObjectURL(url));
    activeObjectUrls = [];

    // Clear content
    setTimeout(() => {
        body().innerHTML = "";
    }, 200);
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
