import { AuthService } from '../api/auth.js';

document.addEventListener('DOMContentLoaded', () => {
    if (AuthService.isAuthenticated()) {
        window.location.href = '/public/index.html';
        return;
    }

    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const errorBox = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const successBox = document.getElementById('successMessage');
    const successText = document.getElementById('successText');

    const showError = (msg) => {
        errorText.textContent = msg;
        errorBox.classList.remove('hidden');
        successBox.classList.add('hidden');
    };

    const showSuccess = (msg) => {
        successText.textContent = msg;
        successBox.classList.remove('hidden');
        errorBox.classList.add('hidden');
    };

    loginBtn.addEventListener('click', async () => {
        const username = usernameInput.value;
        const password = passwordInput.value;

        if (!username || !password) return showError("Please enter both fields.");

        try {
            await AuthService.login(username, password);
            window.location.href = '/public/index.html';
        } catch (error) {
            showError(error.message || "Invalid credentials.");
        }
    });

    registerBtn.addEventListener('click', async () => {
        const username = usernameInput.value;
        const password = passwordInput.value;

        if (!username || !password) return showError("Please enter both fields.");

        try {
            await AuthService.register(username, password);
            showSuccess("Registration successful! You can now sign in.");
            usernameInput.value = '';
            passwordInput.value = '';
        } catch (error) {
            showError(error.message || "Registration failed.");
        }
    });
});