export function initTheme() {
    const savedTheme = localStorage.getItem("jobboard_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
}

export function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
    const nextTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", nextTheme);
    localStorage.setItem("jobboard_theme", nextTheme);
    return nextTheme;
}
