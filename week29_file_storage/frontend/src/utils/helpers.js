/* ═══════════════════════════════════════════════════════════════
   Helpers & Utilities
   ═══════════════════════════════════════════════════════════════ */

/**
 * Format bytes to a human-readable string.
 * @param {number} bytes
 * @returns {string}
 */
export function formatBytes(bytes) {
    if (bytes === 0) return "0 B";
    const units = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    const val = (bytes / Math.pow(1024, i)).toFixed(i === 0 ? 0 : 1);
    return `${val} ${units[i]}`;
}

/**
 * Get a file-type emoji icon based on filename extension or category.
 * @param {string} filename
 * @param {string} category
 * @returns {string}
 */
export function getFileIcon(filename = "", category = "") {
    const ext = filename.split(".").pop().toLowerCase();

    // Specific Extensions
    if (ext === "pdf") return "📕";
    if (["zip", "rar", "tar", "gz", "7z"].includes(ext)) return "🗜️";
    if (["txt", "md", "csv", "json", "js", "py", "html", "css"].includes(ext)) return "📝";
    if (["doc", "docx", "xls", "xlsx", "ppt", "pptx"].includes(ext)) return "📘";
    if (["mp3", "wav", "ogg", "flac"].includes(ext)) return "🎵";
    if (["mp4", "webm", "mkv", "avi"].includes(ext)) return "🎬";
    if (["png", "jpg", "jpeg", "gif", "webp", "svg"].includes(ext)) return "🖼️";

    // Category Fallbacks
    const icons = {
        image: "🖼️",
        document: "📄",
        audio: "🎵",
        video: "🎬",
        other: "📦",
    };
    return icons[category] || "📦";
}

export function getCategoryIcon(category) {
    return getFileIcon("", category);
}

/**
 * Format an ISO date string to a locale-friendly relative date.
 * @param {string} isoDate
 * @returns {string}
 */
export function formatDate(isoDate) {
    const date = new Date(isoDate);
    const now = new Date();
    const diff = now - date;
    const mins = Math.floor(diff / 60000);

    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;

    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}
