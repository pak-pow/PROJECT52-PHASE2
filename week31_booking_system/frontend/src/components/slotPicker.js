/**
 * Dynamic Time Slot Picker Component
 */
export function createSlotPicker({ containerId, onSlotSelect }) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let selectedSlot = null; // { start_time, end_time }

    function render(slots = [], dateStr = "") {
        if (!slots || slots.length === 0) {
            container.innerHTML = `
                <div class="slots-section">
                    <h4>Available Time Slots</h4>
                    <p style="font-size: 0.9rem; color: var(--text-muted);">
                        ${dateStr ? "No open working slots for this date." : "Please select a date on the calendar above."}
                    </p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="slots-section">
                <h4>Available Time Slots (${dateStr})</h4>
                <div class="slots-grid" id="slots-grid">
                    ${slots.map(s => {
                        const isSelected = selectedSlot && selectedSlot.start_time === s.start_time;
                        const isBooked = !s.available;

                        let classes = ["slot-pill"];
                        if (isBooked) classes.push("booked");
                        if (isSelected) classes.push("selected");

                        return `
                            <button type="button" class="${classes.join(" ")}" 
                                    data-start="${s.start_time}" 
                                    data-end="${s.end_time}"
                                    ${isBooked ? "disabled" : ""}>
                                ${s.start_time}
                            </button>
                        `;
                    }).join("")}
                </div>
            </div>
        `;

        const grid = document.getElementById("slots-grid");
        if (grid) {
            grid.addEventListener("click", (e) => {
                const btn = e.target.closest(".slot-pill");
                if (!btn || btn.classList.contains("booked")) return;

                const start_time = btn.dataset.start;
                const end_time = btn.dataset.end;

                selectedSlot = { start_time, end_time };

                grid.querySelectorAll(".slot-pill").forEach(b => b.classList.remove("selected"));
                btn.classList.add("selected");

                if (onSlotSelect) {
                    onSlotSelect(selectedSlot);
                }
            });
        }
    }

    return {
        render,
        getSelectedSlot: () => selectedSlot,
        reset: () => {
            selectedSlot = null;
            render([], "");
        }
    };
}
