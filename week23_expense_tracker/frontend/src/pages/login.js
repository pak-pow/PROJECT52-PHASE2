import { AuthService } from '../api/auth.js';

document.addEventListener('DOMContentLoaded', () => {
    if (AuthService.isAuthenticated()) {
        window.location.href = 'index.html';
        return;
    }

    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const errorBox = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const submitBtn = loginForm.querySelector('button[type="submit"]');

    const showError = (msg) => {
        errorText.textContent = msg;
        errorBox.classList.remove('hidden');
    };

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = usernameInput.value;
        const password = passwordInput.value;

        if (!username || !password) return showError('Please enter both fields.');

        try {
            submitBtn.textContent = 'Signing in...';
            submitBtn.disabled = true;

            await AuthService.login(username, password);
            window.location.href = 'index.html';
        } catch (error) {
            showError(error.message || 'Invalid credentials.');
            submitBtn.textContent = 'Sign In';
            submitBtn.disabled = false;
        }
    });
});