/**
 * helpers.js — Shared utility functions for the SocialFeed frontend.
 */

/**
 * Format an ISO timestamp as a relative time string ("2m ago", "3h ago", "Jul 18").
 */
export function relativeTime(isoString) {
    if (!isoString) return "";
    const date = new Date(isoString);
    const now = Date.now();
    const diffMs = now - date.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHr  = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHr  / 24);

    if (diffSec < 60)  return `${diffSec}s`;
    if (diffMin < 60)  return `${diffMin}m`;
    if (diffHr  < 24)  return `${diffHr}h`;
    if (diffDay < 7)   return `${diffDay}d`;
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

/**
 * Escape HTML special characters to prevent XSS in text nodes.
 */
export function escapeHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

/**
 * Convert plain text to HTML, linkifying @mentions and URLs.
 */
export function linkifyContent(text) {
    return escapeHtml(text)
        .replace(/@(\w+)/g, '<a href="#profile?u=$1" class="mention">@$1</a>')
        .replace(
            /(https?:\/\/[^\s<>"]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer" class="ext-link">$1</a>'
        );
}

/**
 * Format a large number compactly: 1000 → "1K", 1500000 → "1.5M".
 */
export function formatCount(n) {
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, "") + "M";
    if (n >= 1_000)     return (n / 1_000).toFixed(1).replace(/\.0$/, "") + "K";
    return String(n);
}

/**
 * Show a brief toast notification.
 * @param {string} message
 * @param {"info"|"error"|"success"} type
 */
export function showToast(message, type = "info") {
    const toast = document.getElementById("toast");
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast toast--${type}`;
    toast.classList.remove("hidden");
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.add("hidden"), 3000);
}

/**
 * Navigate to a named page and push to history state.
 * Dispatches a custom "navigate" event on window.
 */
export function navigate(page, params = {}) {
    window.dispatchEvent(new CustomEvent("navigate", { detail: { page, params } }));
}

/**
 * Debounce a function call.
 */
export function debounce(fn, delay = 200) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}
