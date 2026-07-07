import { fetchQuizzes, fetchQuiz, submitQuiz, fetchLeaderboard } from "./api/quizApi.js";
import { showView, getTimeTaken }        from "./utils/helpers.js";
import { startTimer, stopTimer }         from "./utils/timer.js";
import { renderCatalog }                 from "./pages/catalog.js";
import { renderQuiz, renderQuestion }    from "./pages/quiz.js";
import { renderResults }                 from "./pages/results.js";
import { renderLeaderboard }             from "./pages/leaderboard.js";
import { openModal, closeModal }         from "./components/modal.js";

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
};

/* ═══════════════════════════════════════════════════════════════
   ORCHESTRATORS
   ═══════════════════════════════════════════════════════════════ */

async function loadCatalog() {
  showView("catalog");
  try {
    const quizzes = await fetchQuizzes();
    renderCatalog(quizzes, startQuiz);
  } catch (err) {
    document.getElementById("quiz-catalog-grid").innerHTML = `
      <p style="color:var(--red);text-align:center;grid-column:1/-1;padding:40px 0;">
        ⚠️ Could not connect to backend. Make sure Flask is running on port 5000.
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
    // Last question answered — stop timer and open modal
    stopTimer(state);
    openModal();
  }
});

// ── Submit username from modal ────────────────────────────────
document.getElementById("btn-submit-username").addEventListener("click", async () => {
  const username = document.getElementById("input-username").value.trim();
  if (!username) {
    document.getElementById("input-username").focus();
    return;
  }

  closeModal();

  try {
    const result = await submitQuiz(state.currentQuiz.id, {
      username,
      answers:    state.answers,
      time_taken: getTimeTaken(state.startTime),
    });
    renderResults(result, state);
    showView("results");
  } catch (err) {
    alert("Something went wrong submitting your quiz. Please try again.");
    console.error(err);
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

// ── View Leaderboard ──────────────────────────────────────────
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

// ── Back to Results (from Leaderboard view) ───────────────────
document.getElementById("btn-back-results").addEventListener("click", () => {
  showView("results");
});

/* ═══════════════════════════════════════════════════════════════
   BOOT
   ═══════════════════════════════════════════════════════════════ */
loadCatalog();
