const API_URL = 'http://127.0.0.1:5000';

// Grabbing the HTML elements
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const loginBtn = document.getElementById('loginBtn');
const dashboardBtn = document.getElementById('dashboardBtn');
const logoutBtn = document.getElementById('logoutBtn');
const outputBox = document.getElementById('output');
const registerBtn = document.getElementById('registerBtn');

async function register() {
    const user = usernameInput.value.trim();
    const pass = passwordInput.value.trim();
    
    if (!user || !pass){
        outputBox.innerHTML = `<span class="text-error">Error:</span> Please enter both username and password!`;
        return;
    }

    outputBox.innerHTML = "Attempting to create account...";
}

async function login() {
    const user = usernameInput.value.trim();
    const pass = passwordInput.value.trim();

    outputBox.innerText = "Attempting to log in...";

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('project52_token', data.token);
            outputBox.innerHTML = `<span class="text-success">Login Success!</span><br>Token saved to localStorage.`;
        } else {
            outputBox.innerHTML = `<span class="text-error">Error:</span> ${data.error}`;
        }
    } catch (error) {
        outputBox.innerText = "Network error. Is your Python server running?";
    }
}

async function accessDashboard() {
    const token = localStorage.getItem('project52_token');

    if (!token) {
        outputBox.innerHTML = `<span class="text-error">Access Denied!</span> No token found. Please log in first.`;
        return;
    }

    outputBox.innerText = "Showing VIP pass to the Bouncer...";

    try {
        const response = await fetch(`${API_URL}/dashboard`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const data = await response.json();

        if (response.ok) {
            outputBox.innerHTML = `<span class="text-success">Access Granted!</span><br>Message: ${data.message}`;
        } else {
            outputBox.innerHTML = `<span class="text-error">Bouncer says:</span> ${data.error}`;
        }
    } catch (error) {
        outputBox.innerText = "Network error communicating with the server.";
    }
}

function logout() {
    localStorage.removeItem('project52_token');
    outputBox.innerHTML = "Logged out. Token deleted from localStorage.";
}

// Event Listeners
loginBtn.addEventListener('click', login);
dashboardBtn.addEventListener('click', accessDashboard);
logoutBtn.addEventListener('click', logout);