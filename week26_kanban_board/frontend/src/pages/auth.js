import { api } from '../api/kanban_api.js';
import { showToast } from '../utils/dom.js';

export function renderAuth(container) {
    // Reset custom board accent overrides to base theme defaults
    document.documentElement.style.removeProperty('--accent');
    document.documentElement.style.removeProperty('--accent-hover');

    let isLogin = true;

    // Helper to update the view state without recreating DOM nodes (to preserve focus)
    function updateState() {
        const titleEl = container.querySelector('#auth-card-title');
        const subtitleEl = container.querySelector('#auth-card-subtitle');
        const submitBtnEl = container.querySelector('#auth-submit-btn');
        const toggleTextEl = container.querySelector('#auth-toggle-text');
        const formEl = container.querySelector('#auth-form');

        // Reset password fields
        formEl.password.value = '';

        if (isLogin) {
            titleEl.textContent = 'Welcome Back';
            subtitleEl.textContent = 'Log in to access your workspaces';
            submitBtnEl.innerHTML = 'Log In <i data-lucide="arrow-right"></i>';
            toggleTextEl.innerHTML = `Don't have an account? <span id="auth-toggle-link" style="color: var(--accent); cursor: pointer; font-weight: 600; text-decoration: underline;">Sign Up</span>`;
        } else {
            titleEl.textContent = 'Create Account';
            subtitleEl.textContent = 'Sign up for your own isolated kanban boards';
            submitBtnEl.innerHTML = 'Create Account <i data-lucide="user-plus"></i>';
            toggleTextEl.innerHTML = `Already have an account? <span id="auth-toggle-link" style="color: var(--accent); cursor: pointer; font-weight: 600; text-decoration: underline;">Log In</span>`;
        }

        if (window.lucide) {
            window.lucide.createIcons();
        }

        // Rebind toggle click
        container.querySelector('#auth-toggle-link').addEventListener('click', () => {
            isLogin = !isLogin;
            updateState();
        });
    }

    container.innerHTML = `
        <div class="auth-page-wrapper" style="
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: calc(100vh - 40px);
            padding: 1.5rem;
        ">
            <div class="auth-card" style="
                background-color: var(--bg-panel);
                border: 1px solid var(--border-color);
                box-shadow: var(--shadow-lg);
                border-radius: var(--radius-lg);
                padding: 2.5rem;
                width: 100%;
                max-width: 420px;
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
            ">
                <div style="text-align: center; display: flex; flex-direction: column; gap: 0.5rem; align-items: center;">
                    <div style="
                        width: 48px;
                        height: 48px;
                        border-radius: var(--radius-md);
                        background-color: rgba(99, 102, 241, 0.1);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: var(--accent);
                        margin-bottom: 0.5rem;
                    ">
                        <i data-lucide="kanban" style="width: 28px; height: 28px;"></i>
                    </div>
                    <h1 id="auth-card-title" style="font-size: 1.75rem; font-weight: 700; color: var(--text-main); margin: 0;">Welcome Back</h1>
                    <p id="auth-card-subtitle" style="color: var(--text-muted); font-size: 0.875rem; margin: 0;">Log in to access your workspaces</p>
                </div>

                <form id="auth-form" style="display: flex; flex-direction: column; gap: 1.25rem;">
                    <div class="form-group" style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <label class="form-label" for="auth-username" style="margin: 0;">Username</label>
                        <input type="text" name="username" id="auth-username" class="form-input" placeholder="Enter username" required autofocus>
                    </div>

                    <div class="form-group" style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <label class="form-label" for="auth-password" style="margin: 0;">Password</label>
                        <input type="password" name="password" id="auth-password" class="form-input" placeholder="••••••••" required>
                    </div>

                    <button type="submit" id="auth-submit-btn" class="btn btn-primary" style="
                        width: 100%;
                        justify-content: center;
                        padding: 0.75rem;
                        font-size: 1rem;
                        margin-top: 0.5rem;
                    ">
                        Log In <i data-lucide="arrow-right"></i>
                    </button>
                </form>

                <div id="auth-toggle-text" style="text-align: center; font-size: 0.875rem; color: var(--text-muted);">
                    Don't have an account? <span id="auth-toggle-link" style="color: var(--accent); cursor: pointer; font-weight: 600; text-decoration: underline;">Sign Up</span>
                </div>
            </div>
        </div>
    `;

    if (window.lucide) {
        window.lucide.createIcons();
    }

    // Set up form submission handler
    const form = container.querySelector('#auth-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = form.username.value.trim();
        const password = form.password.value;

        if (!username || !password) {
            showToast('Username and password are required', 'error');
            return;
        }

        const submitBtn = container.querySelector('#auth-submit-btn');
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';

        try {
            if (isLogin) {
                await api.login(username, password);
                showToast(`Logged in successfully! Welcome, ${username}!`, 'success');
            } else {
                await api.register(username, password);
                showToast(`Account registered and logged in! Welcome, ${username}!`, 'success');
            }
            window.location.hash = '#dashboard';
        } catch (error) {
            showToast(error.message || 'Authentication failed', 'error');
            submitBtn.disabled = false;
            submitBtn.style.opacity = '1';
        }
    });

    // Initial state trigger to bind listeners
    updateState();
}
