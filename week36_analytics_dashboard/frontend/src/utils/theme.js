const THEME_STORAGE_KEY = "analytics_dashboard_theme";

export function initTheme() {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    updateThemeToggleBtn(savedTheme);
}

export function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem(THEME_STORAGE_KEY, newTheme);
    updateThemeToggleBtn(newTheme);
}

function updateThemeToggleBtn(theme) {
    const btn = document.getElementById("theme-toggle-btn");
    if (btn) {
        btn.textContent = theme === "dark" ? "☀️ Light Mode" : "🌙 Dark Mode";
    }
}
