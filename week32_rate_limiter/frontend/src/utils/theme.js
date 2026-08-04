export function initTheme() {
    const savedTheme = localStorage.getItem("limiter_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
}

export function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("limiter_theme", next);
    return next;
}
