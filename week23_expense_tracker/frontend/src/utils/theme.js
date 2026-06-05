// frontend/src/utils/theme.js

export const ThemeManager = {
    init: () => {
        // Check local storage, default to light
        const savedTheme = localStorage.getItem('app_theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        ThemeManager.updateButtonIcon(savedTheme);
        return savedTheme;
    },

    toggle: () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('app_theme', newTheme);
        ThemeManager.updateButtonIcon(newTheme);
        
        return newTheme;
    },

    updateButtonIcon: (theme) => {
        const btn = document.getElementById('themeToggleBtn');
        if (btn) {
            btn.textContent = theme === 'light' ? '🌙' : '☀️';
        }
    }
};
