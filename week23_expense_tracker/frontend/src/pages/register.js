import { AuthService } from '../api/auth.js';

document.addEventListener('DOMContentLoaded', () => {
    if (AuthService.isAuthenticated()) {
        window.location.href = 'index.html';
        return;
    }

    const registerForm = document.getElementById('registerForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const errorBox = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const successBox = document.getElementById('successMessage');
    const successText = document.getElementById('successText');
    const submitBtn = registerForm.querySelector('button[type="submit"]');

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

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = usernameInput.value;
        const password = passwordInput.value;

        if (!username || !password) return showError('Please enter both fields.');

        try {
            submitBtn.textContent = 'Registering...';
            submitBtn.disabled = true;

            await AuthService.register(username, password);

            showSuccess('Registration successful! Redirecting to login...');

            // Give the user 2 seconds to read the success message, then redirect
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);

        } catch (error) {
            showError(error.message || 'Registration failed.');
            submitBtn.textContent = 'Register';
            submitBtn.disabled = false;
        }
    });
});
