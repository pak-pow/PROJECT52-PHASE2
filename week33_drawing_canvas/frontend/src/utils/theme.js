export function initTheme() {
    const savedTheme = localStorage.getItem("canvas_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
}

export function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("canvas_theme", next);
    return next;
}
