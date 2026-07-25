/**
 * theme.js — Light / Dark theme management with persistent storage.
 */
export function initTheme() {
    const savedTheme = localStorage.getItem("sf_theme") ||
        (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");

    setTheme(savedTheme);
}

export function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("sf_theme", theme);
}

export function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    setTheme(next);
    return next;
}
