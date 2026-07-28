import { renderNavbar } from "../components/navbar.js";
import { apiFetchServiceDetail, apiFetchProviderAvailability } from "../api/serviceApi.js";
import { apiCreateBooking } from "../api/bookingApi.js";
import { createCalendar } from "../components/calendar.js";
import { createSlotPicker } from "../components/slotPicker.js";
import { escapeHtml, formatCurrency, formatDate, showToast } from "../utils/helpers.js";
import { isLoggedIn } from "../utils/authCheck.js";

let selectedService = null;
let selectedProviderId = null;
let selectedDateStr = null;
let selectedSlot = null;

document.addEventListener("DOMContentLoaded", () => {
    renderNavbar();

    const urlParams = new URLSearchParams(window.location.search);
    const serviceId = urlParams.get("service_id");

    if (!serviceId) {
        showToast("No service selected.", "error");
        setTimeout(() => window.location.href = "index.html", 1000);
        return;
    }

    initBookingPage(serviceId);
});

async function initBookingPage(serviceId) {
    const slotPicker = createSlotPicker({
        containerId: "slot-picker-container",
        onSlotSelect: (slot) => {
            selectedSlot = slot;
            const summaryTime = document.getElementById("summary-time");
            if (summaryTime) {
                summaryTime.className = "summary-val-highlight";
                summaryTime.textContent = `⏰ ${slot.start_time} - ${slot.end_time}`;
            }
            validateAndToggleSubmit();
        }
    });

    const calendar = createCalendar({
        containerId: "calendar-container",
        onDateSelect: async (dateStr) => {
            selectedDateStr = dateStr;
            selectedSlot = null;
            validateAndToggleSubmit();

            const summaryDate = document.getElementById("summary-date");
            if (summaryDate) {
                summaryDate.className = "summary-val-highlight";
                summaryDate.textContent = `📅 ${formatDate(dateStr)}`;
            }

            const summaryTime = document.getElementById("summary-time");
            if (summaryTime) {
                summaryTime.className = "summary-val-placeholder";
                summaryTime.textContent = "⏰ Select time slot";
            }

            if (!selectedProviderId) {
                showToast("Please select a specialist first.", "error");
                return;
            }

            try {
                const availData = await apiFetchProviderAvailability(selectedProviderId, serviceId, dateStr);
                slotPicker.render(availData.slots, formatDate(dateStr));
                const slotContainer = document.getElementById("slot-picker-container");
                if (slotContainer) {
                    slotContainer.scrollIntoView({ behavior: "smooth", block: "nearest" });
                }
            } catch (err) {
                showToast(err.message, "error");
            }
        }
    });

    try {
        const detail = await apiFetchServiceDetail(serviceId);
        selectedService = detail.service;
        const providers = detail.providers;

        // Render Service Summary
        document.getElementById("service-category").textContent = selectedService.category;
        document.getElementById("service-title").textContent = selectedService.title;
        document.getElementById("service-desc").textContent = selectedService.description;
        document.getElementById("summary-duration").textContent = `${selectedService.duration_minutes} mins`;
        document.getElementById("summary-price").textContent = formatCurrency(selectedService.price);

        function updateProviderBio(provId) {
            const bioBox = document.getElementById("provider-bio");
            if (!bioBox) return;
            const prov = providers.find(p => p.id === provId);
            if (prov && prov.bio) {
                bioBox.textContent = `💡 ${prov.bio}`;
                bioBox.style.display = "block";
            } else {
                bioBox.style.display = "none";
            }
        }

        // Render Provider Dropdown
        const providerSelect = document.getElementById("provider-select");
        if (providers.length === 0) {
            providerSelect.innerHTML = `<option value="">No qualified providers available</option>`;
        } else {
            providerSelect.innerHTML = providers.map(p => `
                <option value="${p.id}">${escapeHtml(p.display_name || p.username)} (${escapeHtml(p.title)})</option>
            `).join("");

            selectedProviderId = providers[0].id;
            updateProviderBio(selectedProviderId);
        }

        providerSelect.addEventListener("change", (e) => {
            selectedProviderId = parseInt(e.target.value);
            updateProviderBio(selectedProviderId);
            selectedDateStr = null;
            selectedSlot = null;
            const summaryDate = document.getElementById("summary-date");
            if (summaryDate) {
                summaryDate.className = "summary-val-placeholder";
                summaryDate.textContent = "📌 Select on calendar";
            }
            const summaryTime = document.getElementById("summary-time");
            if (summaryTime) {
                summaryTime.className = "summary-val-placeholder";
                summaryTime.textContent = "⏰ Select time slot";
            }
            calendar.reset();
            slotPicker.reset();
            validateAndToggleSubmit();
        });

    } catch (err) {
        showToast(err.message, "error");
    }

    // Attach Confirm Booking Event
    const confirmBtn = document.getElementById("btn-confirm-booking");
    if (confirmBtn) {
        confirmBtn.addEventListener("click", async () => {
            if (!isLoggedIn()) {
                showToast("Please log in to complete your booking.", "error");
                setTimeout(() => window.location.href = "login.html", 1000);
                return;
            }

            if (!selectedService || !selectedProviderId || !selectedDateStr || !selectedSlot) {
                showToast("Please complete all booking selections.", "error");
                return;
            }

            const notesInput = document.getElementById("booking-notes");
            const notes = notesInput ? notesInput.value.trim() : "";

            confirmBtn.disabled = true;
            confirmBtn.textContent = "Processing Booking...";

            try {
                await apiCreateBooking({
                    provider_id: selectedProviderId,
                    service_id: selectedService.id,
                    booking_date: selectedDateStr,
                    start_time: selectedSlot.start_time,
                    end_time: selectedSlot.end_time,
                    notes: notes
                });

                showToast("🎉 Appointment confirmed successfully!", "success");
                setTimeout(() => {
                    window.location.href = "dashboard.html";
                }, 1200);
            } catch (err) {
                showToast(err.message, "error");
                confirmBtn.disabled = false;
                confirmBtn.textContent = "Confirm & Reserve Appointment ➔";
            }
        });
    }
}

function validateAndToggleSubmit() {
    const confirmBtn = document.getElementById("btn-confirm-booking");
    if (!confirmBtn) return;

    const isValid = selectedService && selectedProviderId && selectedDateStr && selectedSlot;
    confirmBtn.disabled = !isValid;
}
