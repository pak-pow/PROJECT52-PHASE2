/**
 * Interactive Month-View Calendar Component
 */
export function createCalendar({ containerId, onDateSelect }) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let currentDate = new Date(); // Current viewing month
    let selectedDateStr = null;

    function render() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth(); // 0-indexed

        const monthName = currentDate.toLocaleString("en-US", { month: "long", year: "numeric" });

        // First day of month (0 = Sun, 1 = Mon, etc.)
        const firstDay = new Date(year, month, 1).getDay();
        // Days in month
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        const today = new Date();
        const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

        container.innerHTML = `
            <div class="calendar-header">
                <button id="cal-prev-month" class="month-nav-btn" aria-label="Previous Month">❮</button>
                <div class="month-title">${monthName}</div>
                <button id="cal-next-month" class="month-nav-btn" aria-label="Next Month">❯</button>
            </div>

            <div class="calendar-weekdays">
                <div>Sun</div><div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div>
            </div>

            <div class="calendar-days-grid" id="calendar-days">
                ${generateDaysHtml(year, month, firstDay, daysInMonth, todayStr, selectedDateStr)}
            </div>
        `;

        // Attach Month Nav Events
        document.getElementById("cal-prev-month").addEventListener("click", () => {
            currentDate.setMonth(currentDate.getMonth() - 1);
            render();
        });

        document.getElementById("cal-next-month").addEventListener("click", () => {
            currentDate.setMonth(currentDate.getMonth() + 1);
            render();
        });

        // Attach Day Cell Click Event
        const daysGrid = document.getElementById("calendar-days");
        daysGrid.addEventListener("click", (e) => {
            const cell = e.target.closest(".calendar-day-cell");
            if (!cell || cell.classList.contains("disabled") || cell.classList.contains("empty")) return;

            const dateVal = cell.dataset.date;
            selectedDateStr = dateVal;

            daysGrid.querySelectorAll(".calendar-day-cell").forEach(c => c.classList.remove("selected"));
            cell.classList.add("selected");

            if (onDateSelect) {
                onDateSelect(dateVal);
            }
        });
    }

    render();

    return {
        getSelectedDate: () => selectedDateStr,
        reset: () => {
            selectedDateStr = null;
            render();
        }
    };
}

function generateDaysHtml(year, month, firstDay, daysInMonth, todayStr, selectedDateStr) {
    let html = "";

    // Empty cells for alignment before day 1
    for (let i = 0; i < firstDay; i++) {
        html += `<div class="calendar-day-cell empty"></div>`;
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (let day = 1; day <= daysInMonth; day++) {
        const dayObj = new Date(year, month, day);
        const dayOfWeek = dayObj.getDay(); // 0=Sun, 6=Sat
        const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

        // Disable weekends (Sat/Sun: 0 or 6) and past dates
        const isPast = dayObj < today;
        const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
        const isDisabled = isPast || isWeekend;

        const isToday = dateStr === todayStr;
        const isSelected = dateStr === selectedDateStr;

        let classes = ["calendar-day-cell"];
        if (isDisabled) classes.push("disabled");
        if (isToday) classes.push("today");
        if (isSelected) classes.push("selected");

        html += `
            <div class="${classes.join(" ")}" data-date="${dateStr}">
                ${day}
            </div>
        `;
    }

    return html;
}
