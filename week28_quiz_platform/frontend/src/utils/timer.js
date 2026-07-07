const CIRCUMFERENCE = 326.73; // 2 * Math.PI * 52

export function startTimer(seconds, state, onExpire) {
    state.timeLeft  = seconds;
    state.totalTime = seconds;
    state.startTime = Date.now();

    const display = document.getElementById("timer-display");
    const circle  = document.getElementById("timer-circle");
    const wrapper = document.querySelector(".timer-wrapper");

    // Reset ring
    circle.style.strokeDashoffset = 0;
    wrapper.classList.remove("danger");

    state.timerInterval = setInterval(() => {
        state.timeLeft--;

        display.textContent = state.timeLeft;

        const offset = CIRCUMFERENCE * (1 - state.timeLeft / state.totalTime);
        circle.style.strokeDashoffset = offset;

        if (state.timeLeft <= 10) {
            wrapper.classList.add("danger");
        }

        if (state.timeLeft <= 0) {
            stopTimer(state);
            onExpire();
        }
    }, 1000);
}

export function stopTimer(state) {
    if (state.timerInterval) {
        clearInterval(state.timerInterval);
        state.timerInterval = null;
    }
}