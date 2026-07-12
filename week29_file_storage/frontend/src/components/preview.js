/* ═══════════════════════════════════════════════════════════════
   Preview Modal Component
   ═══════════════════════════════════════════════════════════════ */

import { thumbnailUrl, downloadUrl } from "../api/fileApi.js";
import { formatBytes, formatDate, getCategoryIcon } from "../utils/helpers.js";

const overlay = () => document.getElementById("preview-modal");
const body = () => document.getElementById("modal-body");


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

    const isImage = file.category === "image" && file.has_thumbnail;
    const token = localStorage.getItem("fv_token");

    content.innerHTML = `
        <div class="modal-preview">
            ${isImage
                ? `<img src="${thumbnailUrl(file.id)}" alt="${escapeHtml(file.original_name)}"
                        onerror="this.outerHTML='<span class=\\'no-preview-icon\\'>${getCategoryIcon(file.category)}</span>'" />`
                : `<span class="no-preview-icon">${getCategoryIcon(file.category)}</span>`
            }
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

    // Attach auth header to download link via fetch
    const dlBtn = content.querySelector("#modal-download-btn");
    dlBtn.addEventListener("click", async (e) => {
        e.preventDefault();
        try {
            const resp = await fetch(downloadUrl(file.id), {
                headers: { Authorization: `Bearer ${token}` },
            });
            const blob = await resp.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = file.original_name;
            a.click();
            URL.revokeObjectURL(url);
        } catch { /* fail silently */ }
    });

    // Fetch full-size image instead of thumbnail for preview
    if (isImage) {
        const img = content.querySelector(".modal-preview img");
        fetch(downloadUrl(file.id), {
            headers: { Authorization: `Bearer ${token}` },
        })
        .then(r => r.blob())
        .then(blob => { img.src = URL.createObjectURL(blob); })
        .catch(() => {});
    }

    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
}


export function closePreview() {
    const modal = overlay();
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
}


function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
