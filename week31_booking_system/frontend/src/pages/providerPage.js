import { renderNavbar } from "../components/navbar.js";
import { apiFetchProviders, apiFetchProviderAvailability } from "../api/serviceApi.js";
import { escapeHtml, formatDate, showToast } from "../utils/helpers.js";

let providersList = [];
let selectedProviderId = null;
let selectedDateStr = new Date().toISOString().split("T")[0]; // Defaults to today

document.addEventListener("DOMContentLoaded", async () => {
    renderNavbar();
    await initProviderAgendaPage();
});

async function initProviderAgendaPage() {
    const dateInput = document.getElementById("date-select-agenda");
    if (dateInput) {
        dateInput.value = selectedDateStr;
        dateInput.addEventListener("change", (e) => {
            selectedDateStr = e.target.value;
            loadAgendaTimeline();
        });
    }

    try {
        providersList = await apiFetchProviders();
        const providerSelect = document.getElementById("provider-select-agenda");
        if (!providerSelect) return;

        if (providersList.length === 0) {
            providerSelect.innerHTML = `<option value="">No specialists found</option>`;
            return;
        }

        providerSelect.innerHTML = providersList.map(p => `
            <option value="${p.id}">${escapeHtml(p.display_name || p.username)} (${escapeHtml(p.title)})</option>
        `).join("");

        selectedProviderId = providersList[0].id;
        updateHeaderInfo(providersList[0]);

        providerSelect.addEventListener("change", (e) => {
            selectedProviderId = parseInt(e.target.value);
            const prov = providersList.find(p => p.id === selectedProviderId);
            if (prov) updateHeaderInfo(prov);
            loadAgendaTimeline();
        });

        await loadAgendaTimeline();
    } catch (err) {
        showToast(err.message, "error");
    }
}

function updateHeaderInfo(provider) {
    const nameHeader = document.getElementById("provider-name-header");
    const titleHeader = document.getElementById("provider-title-header");

    if (nameHeader) nameHeader.textContent = `${provider.display_name || provider.username}'s Agenda`;
    if (titleHeader) titleHeader.textContent = `${provider.title} • ${provider.bio || "Specialist Schedule"}`;
}

async function loadAgendaTimeline() {
    const timeline = document.getElementById("agenda-timeline");
    const dateTitle = document.getElementById("agenda-date-title");
    const dateSubtitle = document.getElementById("agenda-date-subtitle");

    if (!timeline || !selectedProviderId) return;

    if (dateTitle) dateTitle.textContent = `Schedule Agenda — ${formatDate(selectedDateStr)}`;
    if (dateSubtitle) dateSubtitle.textContent = `Daily time slots and appointment status for ${formatDate(selectedDateStr)}`;

    timeline.innerHTML = `
        <div class="agenda-slot-row skeleton" style="height: 70px;"></div>
        <div class="agenda-slot-row skeleton" style="height: 70px;"></div>
    `;

    try {
        // Fetch provider availability grid for selected date (service_id=0 or 1 for general slot grid)
        const availData = await apiFetchProviderAvailability(selectedProviderId, 1, selectedDateStr);
        const slots = availData.slots || [];

        if (slots.length === 0) {
            timeline.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📅</div>
                    <h3>No Scheduled Slots</h3>
                    <p>This specialist is not scheduled to work on ${formatDate(selectedDateStr)} (Weekends / Off-Days).</p>
                </div>
            `;
            return;
        }

        timeline.innerHTML = slots.map(s => {
            const isBooked = !s.available;

            if (isBooked) {
                return `
                    <div class="agenda-slot-row">
                        <div class="agenda-time">⏰ ${s.start_time} - ${s.end_time}</div>
                        <div class="agenda-client-info">
                            <div class="client-name">Reserved Appointment</div>
                            <div class="service-name">Confidential Client Appointment</div>
                        </div>
                        <span class="status-badge status-confirmed">✅ Booked</span>
                    </div>
                `;
            } else {
                return `
                    <div class="agenda-slot-empty">
                        <div class="empty-time">⏰ ${s.start_time} - ${s.end_time}</div>
                        <div class="empty-lbl">Available Slot</div>
                    </div>
                `;
            }
        }).join("");

    } catch (err) {
        showToast(err.message, "error");
        timeline.innerHTML = `<p style="color: var(--danger);">Failed to load schedule agenda.</p>`;
    }
}
