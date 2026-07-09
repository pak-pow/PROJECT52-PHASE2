import { escapeHtml } from "../utils/helpers.js";

/* ── HTML Template ───────────────────────────────────────────── */
export const QUIZ_HTML = `
  <header class="quiz-header">
    <div class="quiz-header-inner">
      <button id="btn-quit-quiz" class="btn-quit" title="Quit quiz">&#8592; Quit</button>
      <span id="quiz-header-title" class="quiz-header-title">Quiz</span>
      <span id="quiz-progress-label" class="quiz-progress-label">1 / 5</span>
    </div>
    <div class="progress-track">
      <div id="progress-bar" class="progress-bar" style="width: 0%"></div>
    </div>
  </header>

  <main class="quiz-main">
    <div class="timer-wrapper">
      <svg class="timer-ring" viewBox="0 0 120 120" id="timer-svg">
        <defs>
          <linearGradient id="timer-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="var(--blue)" />
            <stop offset="100%" stop-color="var(--purple)" />
          </linearGradient>
        </defs>
        <circle class="timer-ring-bg" cx="60" cy="60" r="52" />
        <circle class="timer-ring-fg" cx="60" cy="60" r="52" id="timer-circle" style="stroke: url(#timer-gradient);" />
      </svg>
      <div class="timer-center">
        <span id="timer-display" class="timer-number">60</span>
        <span class="timer-label">sec</span>
      </div>
    </div>

    <div class="question-card" id="question-card">
      <p class="question-number" id="question-number">Question 1</p>
      <h2 class="question-text" id="question-text">Loading...</h2>
      <div class="options-grid" id="options-grid"></div>
    </div>

    <div class="quiz-nav">
      <button id="btn-next" class="btn-primary" disabled>Next Question &#8594;</button>
    </div>
  </main>
`;

/* ── Renderers ───────────────────────────────────────────────── */
export function renderQuiz(quiz, state) {

  // Reset state for a fresh quiz run
  state.currentQuiz          = quiz;
  state.questions            = quiz.questions;
  state.currentQuestionIndex = 0;
  state.answers              = [];

  // Set the quiz title in the sticky header
  document.getElementById("quiz-header-title").textContent = quiz.title;
}

export function renderQuestion(index, state) {
  const question = state.questions[index];
  const total    = state.questions.length;

  // Update sticky header progress
  document.getElementById("quiz-progress-label").textContent = `${index + 1} / ${total}`;
  document.getElementById("progress-bar").style.width = `${((index + 1) / total) * 100}%`;

  // Update question card content
  document.getElementById("question-number").textContent = `Question ${index + 1}`;
  document.getElementById("question-text").textContent   = question.question_text;

  // Rebuild options grid
  const grid = document.getElementById("options-grid");
  grid.innerHTML = question.options
    .map(
      (opt, i) =>
        `<button class="option-btn" id="opt-${i}" data-index="${i}">${escapeHtml(opt)}</button>`
    )
    .join("");


  // Reset Next button
  const btnNext       = document.getElementById("btn-next");
  btnNext.disabled    = true;
  btnNext.textContent = index === total - 1 ? "Submit Answers →" : "Next Question →";

  // Option click — highlight selection and unlock Next
  grid.querySelectorAll(".option-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      grid.querySelectorAll(".option-btn").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
      btnNext.disabled = false;
    });
  });
}
