import { renderNavbar } from "../components/navbar.js";
import { apiFetchMyBookings, apiCancelBooking } from "../api/bookingApi.js";
import { isLoggedIn, getCurrentUser } from "../utils/authCheck.js";
import { escapeHtml, formatCurrency, formatDate, showToast } from "../utils/helpers.js";

let allBookings = [];
let currentTab = "upcoming";

document.addEventListener("DOMContentLoaded", () => {
    if (!isLoggedIn()) {
        showToast("Please log in to view your appointments.", "error");
        setTimeout(() => window.location.href = "login.html", 600);
        return;
    }

    renderNavbar();
    initDashboard();
});

async function initDashboard() {
    const user = getCurrentUser();
    const welcomeTitle = document.getElementById("welcome-title");
    if (welcomeTitle && user) {
        welcomeTitle.textContent = `${user.display_name || user.username}'s Appointments`;
    }

    initTabs();
    await loadAppointments();
}

function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            currentTab = btn.dataset.tab;
            renderAppointmentsGrid();
        });
    });
}

async function loadAppointments() {
    const grid = document.getElementById("appointments-grid");
    if (!grid) return;

    grid.innerHTML = `
        <div class="appointment-card skeleton" style="height: 220px;"></div>
        <div class="appointment-card skeleton" style="height: 220px;"></div>
    `;

    try {
        allBookings = await apiFetchMyBookings();
        updateStats();
        renderAppointmentsGrid();
    } catch (err) {
        showToast(err.message, "error");
        grid.innerHTML = `<p style="color: var(--danger); grid-column: 1 / -1;">Failed to load appointments.</p>`;
    }
}

function getCategorizedBookings() {
    const todayStr = new Date().toISOString().split("T")[0];

    const upcomingList = allBookings.filter(b => {
        return b.status === "confirmed" && b.booking_date >= todayStr;
    });

    const pastList = allBookings.filter(b => {
        return b.status === "confirmed" && b.booking_date < todayStr;
    });

    const cancelledList = allBookings.filter(b => {
        return b.status === "cancelled";
    });

    return { upcomingList, pastList, cancelledList, todayStr };
}

function updateStats() {
    const { upcomingList, pastList, cancelledList } = getCategorizedBookings();

    document.getElementById("stat-total").textContent = allBookings.length;
    document.getElementById("stat-upcoming").textContent = upcomingList.length;
    document.getElementById("count-upcoming").textContent = upcomingList.length;
    document.getElementById("count-past").textContent = pastList.length;
    document.getElementById("count-cancelled").textContent = cancelledList.length;
}

function renderAppointmentsGrid() {
    const grid = document.getElementById("appointments-grid");
    if (!grid) return;

    const { upcomingList, pastList, cancelledList, todayStr } = getCategorizedBookings();

    let activeList = [];
    if (currentTab === "upcoming") activeList = upcomingList;
    else if (currentTab === "past") activeList = pastList;
    else if (currentTab === "cancelled") activeList = cancelledList;

    if (activeList.length === 0) {
        let label = "Upcoming";
        let icon = "📅";
        let desc = "You don't have any active upcoming reservations. Browse our service catalog to book an appointment.";
        if (currentTab === "past") {
            label = "Past";
            icon = "🎉";
            desc = "No completed past appointments found.";
        } else if (currentTab === "cancelled") {
            label = "Cancelled";
            icon = "🚫";
            desc = "No cancelled appointments found.";
        }

        grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">${icon}</div>
                <h3>No ${label} Appointments</h3>
                <p>${desc}</p>
                ${currentTab === "upcoming" ? `<a href="index.html" class="btn-primary">Browse Services ➔</a>` : ""}
            </div>
        `;
        return;
    }

    grid.innerHTML = activeList.map(b => {
        const isCancelled = b.status === "cancelled";
        const isPast = b.booking_date < todayStr;
        const isUpcoming = b.status === "confirmed" && !isPast;

        let statusClass = "status-confirmed";
        let statusText = "✅ Confirmed";

        if (isCancelled) {
            statusClass = "status-cancelled";
            statusText = "🚫 Cancelled";
        } else if (isPast) {
            statusClass = "status-completed";
            statusText = "🎉 Completed";
        }

        return `
            <div class="appointment-card ${isCancelled ? "card-cancelled" : ""}" data-booking-id="${b.id}">
                <div>
                    <div class="card-header-row">
                        <span class="card-badge">${escapeHtml(b.service_category || "Service")}</span>
                        <span class="status-badge ${statusClass}">
                            ${statusText}
                        </span>
                    </div>
                    <h3 class="app-service-title">${escapeHtml(b.service_title)}</h3>
                    <p class="app-provider-name">👤 ${escapeHtml(b.provider_name)} (${escapeHtml(b.provider_title)})</p>

                    <div class="app-datetime-box">
                        <span class="datetime-date">📅 ${formatDate(b.booking_date)}</span>
                        <span class="datetime-time">⏰ ${b.start_time} - ${b.end_time}</span>
                    </div>

                    ${b.notes ? `<p class="app-notes">💬 "${escapeHtml(b.notes)}"</p>` : ""}
                </div>

                <div class="app-card-footer">
                    <span class="app-price">${formatCurrency(b.price)}</span>
                    ${isUpcoming ? `
                        <button class="btn-danger btn-cancel-booking" data-booking-id="${b.id}">
                            Cancel Appointment
                        </button>
                    ` : ""}
                </div>
            </div>
        `;
    }).join("");

    // Attach Cancellation Click Handlers
    grid.querySelectorAll(".btn-cancel-booking").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const bookingId = parseInt(e.target.dataset.bookingId);
            if (!confirm("Are you sure you want to cancel this appointment?")) return;

            btn.disabled = true;
            btn.textContent = "Cancelling...";

            try {
                await apiCancelBooking(bookingId);
                showToast("Appointment cancelled successfully.", "success");
                await loadAppointments();
            } catch (err) {
                showToast(err.message, "error");
                btn.disabled = false;
                btn.textContent = "Cancel Appointment";
            }
        });
    });
}
