const API_BASE_URL = "http://127.0.0.1:5000/api";

export async function loginUser(email, password) {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Invalid email or password.");
    }
    return await res.json();
}

export async function registerUser(userData) {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userData)
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Failed to create account.");
    }
    return await res.json();
}
