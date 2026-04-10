const API_URL = 'http://127.0.0.1:5000';

// Grabbing the HTML elements
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const loginBtn = document.getElementById('loginBtn');
const logoutBtn = document.getElementById('logoutBtn');
const outputBox = document.getElementById('output');
const registerBtn = document.getElementById('registerBtn');

const authSection = document.getElementById('auth-section');
const dashboardSection = document.getElementById('dashboard-section');
const profileId = document.getElementById('profile-id');
const profileUser = document.getElementById('profile-user');

const oldPasswordInput = document.getElementById('old-password');
const newPasswordInput = document.getElementById('new-password');
const changePasswordBtn = document.getElementById('changePasswordBtn');

async function register() {
    const user = usernameInput.value.trim();
    const pass = passwordInput.value.trim();
    
    if (!user || !pass){
        outputBox.innerHTML = `<span class="text-error">Error:</span> Please enter both username and password!`;
        return;
    }

    outputBox.innerHTML = "Attempting to create account...";

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ username: user, password: pass})
        });

        const data = await response.json();

        // 201 is our specific HTTP status code for "Created"
        if (response.status === 201) {
            outputBox.innerHTML = `<span class="text-success">Account Created!</span><br>Welcome ${user}. You may now log in.`;
            // Clear the inputs to look clean
            usernameInput.value = '';
            passwordInput.value = '';
        } else {
            // This will catch our 409 Conflict if the username is already taken
            outputBox.innerHTML = `<span class="text-error">Registration Failed:</span> ${data.error}`;
        }
    } catch (error) {
        outputBox.innerText = "Network error communicating with the server..."
    }
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

            checkAuthState()
        } else {
            outputBox.innerHTML = `<span class="text-error">Error:</span> ${data.error}`;
        }
    } catch (error) {
        outputBox.innerText = "Network error. Is your Python server running?";
    }
}

async function checkAuthState() {
    const token = localStorage.getItem('project52_token');

    if (!token) {
        // NO TOKEN: Show Auth, Hide Dashboard
        authSection.classList.remove('hidden');
        dashboardSection.classList.add('hidden');
        outputBox.innerText = "Please log in or create an account.";
        return;
    }

    // TOKEN FOUND: Attempt to fetch the secure dashboard data
    try {
        const response = await fetch(`${API_URL}/dashboard`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const data = await response.json();

        if (response.ok) {
            // SUCCESS: Token is valid Show Dashboard, Hide Auth
            authSection.classList.add('hidden');
            dashboardSection.classList.remove('hidden');
            
            // Populate the Profile Card with real database data!
            profileId.innerText = data.user_data.id;
            profileUser.innerText = data.user_data.username;
            
            outputBox.innerHTML = `<span class="text-success">Welcome back!</span>`;
        } else {
            // TOKEN INVALID OR EXPIRED: Kick them out
            logout();
            outputBox.innerHTML = `<span class="text-error">Session Expired:</span> Please log in again.`;
        }
    } catch (error) {
        outputBox.innerText = "Network error communicating with the server.";
    }
}

async function changePassword() {
    const oldPass = oldPasswordInput.value.trim();
    const newPass = newPasswordInput.value.trim();
    const token = localStorage.getItem('project52_token');

    if (!oldPass || !newPass) {
        outputBox.innerHTML = `<span class="text-error">Error:</span> Please fill in both password fields!`;
        return;
    }

    outputBox.innerText = "Updating password...";

    try {
        const response = await fetch(`${API_URL}/change-password`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` 
            },
            body: JSON.stringify({ old_password: oldPass, new_password: newPass })
        });

        const data = await response.json();

        if (response.ok) {
            outputBox.innerHTML = `<span class="text-success">Success!</span> ${data.message}`;
            oldPasswordInput.value = '';
            newPasswordInput.value = '';
        } else {
            outputBox.innerHTML = `<span class="text-error">Update Failed:</span> ${data.error}`;
        }
    } catch (error) {
        outputBox.innerText = "Network error communicating with the server.";
    }
}

function logout() {
    localStorage.removeItem('project52_token');
    checkAuthState();
    outputBox.innerHTML = "Logged out successfully.";
}

// Event Listeners
loginBtn.addEventListener('click', login);
registerBtn.addEventListener('click', register);
logoutBtn.addEventListener('click', logout);
changePasswordBtn.addEventListener('click', changePassword);

checkAuthState();