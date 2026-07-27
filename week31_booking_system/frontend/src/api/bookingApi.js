import { getToken } from "../utils/authCheck.js";

const API_BASE = "http://127.0.0.1:5000/api";

export async function apiCreateBooking(bookingData) {
    const token = getToken();
    if (!token) throw new Error("Authentication required. Please log in first.");

    const res = await fetch(`${API_BASE}/bookings`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(bookingData),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to confirm booking.");
    return data.booking;
}

export async function apiFetchMyBookings() {
    const token = getToken();
    if (!token) throw new Error("Authentication required.");

    const res = await fetch(`${API_BASE}/bookings/my-bookings`, {
        headers: { "Authorization": `Bearer ${token}` }
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to fetch appointments.");
    return data.bookings;
}

export async function apiCancelBooking(bookingId) {
    const token = getToken();
    if (!token) throw new Error("Authentication required.");

    const res = await fetch(`${API_BASE}/bookings/${bookingId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to cancel appointment.");
    return data;
}
