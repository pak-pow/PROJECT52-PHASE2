/**
 * formatters.js — pure data-formatting helpers, no DOM dependencies.
 */

/**
 * Formats an ISO timestamp string into a human-readable date.
 * e.g. "2026-06-19T12:00:00" → "June 19, 2026"
 * @param {string} isoString
 * @returns {string}
 */
export function formatDate(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return isoString;
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

/**
 * Truncates a string to maxLen characters, appending '…' if cut.
 * @param {string} str
 * @param {number} maxLen
 * @returns {string}
 */
export function truncate(str, maxLen = 120) {
    if (!str) return '';
    return str.length > maxLen ? str.slice(0, maxLen).trimEnd() + '…' : str;
}

/**
 * Converts a recipe title into a URL-safe slug.
 * e.g. "Honey Garlic Butter Salmon" → "honey-garlic-butter-salmon"
 * @param {string} title
 * @returns {string}
 */
export function slugify(title) {
    return title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
}
