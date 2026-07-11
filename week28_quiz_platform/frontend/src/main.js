import { fetchQuizzes, fetchQuiz, submitQuiz, fetchLeaderboard } from "./api/quizApi.js";
import { showView, getTimeTaken }        from "./utils/helpers.js";
import { startTimer, stopTimer }         from "./utils/timer.js";
import { CATALOG_HTML, renderCatalog }              from "./pages/catalog.js";
import { QUIZ_HTML, renderQuiz, renderQuestion }    from "./pages/quiz.js";
import { RESULTS_HTML, renderResults }              from "./pages/results.js";
import { LEADERBOARD_HTML, renderLeaderboard }      from "./pages/leaderboard.js";
import { MODAL_HTML, openModal, closeModal }        from "./components/modal.js";

/* ═══════════════════════════════════════════════════════════════
   BOOT — Inject HTML templates into view shells
   Must happen before any event listeners or DOM queries below.
   ═══════════════════════════════════════════════════════════════ */
document.getElementById("view-catalog").innerHTML     = CATALOG_HTML;
document.getElementById("view-quiz").innerHTML        = QUIZ_HTML;
document.getElementById("view-results").innerHTML     = RESULTS_HTML;
document.getElementById("view-leaderboard").innerHTML = LEADERBOARD_HTML;
document.getElementById("modal-container").innerHTML  = MODAL_HTML;

/* ═══════════════════════════════════════════════════════════════
   STATE — single source of truth for the entire app
   ═══════════════════════════════════════════════════════════════ */
const state = {
  currentQuiz:          null,
  questions:            [],
  currentQuestionIndex: 0,
  answers:              [],
  timerInterval:        null,
  timeLeft:             0,
  startTime:            null,
  totalTime:            0,
  lastResult:           null,
  isSubmitting:         false,   // guard against double-submit
};

/* ═══════════════════════════════════════════════════════════════
   ORCHESTRATORS
   ═══════════════════════════════════════════════════════════════ */

async function loadCatalog() {
  state.isSubmitting = false;
  showView("catalog");
  try {
    const quizzes = await fetchQuizzes();
    renderCatalog(quizzes, startQuiz);
  } catch (err) {
    document.getElementById("quiz-catalog-grid").innerHTML = `
      <p style="color:var(--red);text-align:center;grid-column:1/-1;padding:40px 0;">
        Could not connect to backend. Make sure Flask is running on port 5000.
      </p>`;
    console.error(err);
  }
}

async function startQuiz(id) {
  try {
    const quiz = await fetchQuiz(id);
    renderQuiz(quiz, state);
    showView("quiz");
    renderQuestion(0, state);
    startTimer(quiz.time_limit_seconds, state, handleTimerExpire);
  } catch (err) {
    alert("Failed to load quiz. Make sure the backend is running.");
    console.error(err);
  }
}

function handleTimerExpire() {
  // Fill any unanswered questions with -1
  while (state.answers.length < state.questions.length) {
    state.answers.push(-1);
  }
  openModal();
}

/* ═══════════════════════════════════════════════════════════════
   EVENT LISTENERS
   ═══════════════════════════════════════════════════════════════ */

// ── Next / Submit button ──────────────────────────────────────
document.getElementById("btn-next").addEventListener("click", () => {
  const selected = document.querySelector(".option-btn.selected");
  if (!selected) return;

  state.answers.push(parseInt(selected.dataset.index));

  const nextIndex = state.currentQuestionIndex + 1;

  if (nextIndex < state.questions.length) {
    state.currentQuestionIndex = nextIndex;
    renderQuestion(nextIndex, state);
  } else {
    // Last question — stop timer and open username modal
    stopTimer(state);
    openModal();
  }
});

// ── Submit username from modal ────────────────────────────────
document.getElementById("btn-submit-username").addEventListener("click", async () => {
  // Guard: prevent double-submit
  if (state.isSubmitting) return;

  const username = document.getElementById("input-username").value.trim();
  if (!username) {
    document.getElementById("input-username").focus();
    return;
  }

  // Lock UI during async call
  state.isSubmitting = true;
  const submitBtn = document.getElementById("btn-submit-username");
  submitBtn.disabled    = true;
  submitBtn.textContent = "Submitting...";

  closeModal();

  try {
    const result = await submitQuiz(state.currentQuiz.id, {
      username,
      answers:    state.answers,
      time_taken: getTimeTaken(state.startTime),
    });
    renderResults(result, state);
    showView("results");
    state.isSubmitting = false;
  } catch (err) {
    // Re-open modal so user can retry
    openModal();
    submitBtn.disabled    = false;
    submitBtn.textContent = "Submit Answers \u2192";
    state.isSubmitting    = false;
    console.error("Submit failed:", err);
    alert("Something went wrong submitting your quiz. Please try again.");
  }
});

// ── Enter key inside username input ──────────────────────────
document.getElementById("input-username").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    document.getElementById("btn-submit-username").click();
  }
});

// ── Quit quiz ─────────────────────────────────────────────────
document.getElementById("btn-quit-quiz").addEventListener("click", () => {
  stopTimer(state);
  loadCatalog();
});

// ── View Leaderboard (from Results) ──────────────────────────
document.getElementById("btn-view-leaderboard").addEventListener("click", async () => {
  try {
    const data = await fetchLeaderboard(state.currentQuiz.id);
    renderLeaderboard(data, state);
    showView("leaderboard");
  } catch (err) {
    alert("Failed to load leaderboard.");
    console.error(err);
  }
});

// ── Play Again (from Results view) ───────────────────────────
document.getElementById("btn-play-again-results").addEventListener("click", loadCatalog);

// ── Play Another Quiz (from Leaderboard view) ─────────────────
document.getElementById("btn-play-again-lb").addEventListener("click", loadCatalog);

// ── Keyboard Shortcuts (1-4, Enter) for Quiz View ────────────
window.addEventListener("keydown", (e) => {
  const quizView = document.getElementById("view-quiz");
  if (!quizView || !quizView.classList.contains("active")) return;

  // If username modal is open, ignore quiz keyboard shortcuts
  const modal = document.getElementById("modal-username");
  if (modal && !modal.classList.contains("hidden")) return;

  // 1-4 keys to select option buttons
  if (e.key >= "1" && e.key <= "4") {
    const optIndex = parseInt(e.key) - 1;
    const optBtn = document.getElementById(`opt-${optIndex}`);
    if (optBtn) {
      optBtn.click();
    }
  }

  // Enter key to click Next/Submit
  if (e.key === "Enter") {
    const btnNext = document.getElementById("btn-next");
    if (btnNext && !btnNext.disabled) {
      btnNext.click();
    }
  }
});

// ── Back to Results (from Leaderboard view) ───────────────────
document.getElementById("btn-back-results").addEventListener("click", () => {
  showView("results");
});

/* ═══════════════════════════════════════════════════════════════
   INIT
   ═══════════════════════════════════════════════════════════════ */
loadCatalog();
