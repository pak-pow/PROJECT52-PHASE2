/**
 * Escapes HTML to prevent XSS in chat and usernames.
 */
export function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * Renders toast notification.
 */
export function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3500);
}

/**
 * Retrieves query string parameter value.
 */
export function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

/**
 * Exports current canvas artwork as high-resolution PNG file download.
 */
export function exportCanvasToPng(canvasElement, roomCode = "ARTWORK") {
    if (!canvasElement) return;

    try {
        const dataUrl = canvasElement.toDataURL("image/png");
        const link = document.createElement("a");
        link.download = `CanvasSync_${roomCode}_${Date.now()}.png`;
        link.href = dataUrl;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showToast("Artwork exported as PNG! 🎨", "success");
    } catch (e) {
        showToast("Failed to export artwork image.", "error");
    }
}
