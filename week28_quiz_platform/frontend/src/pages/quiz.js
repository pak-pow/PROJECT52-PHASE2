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
        `<button class="option-btn" id="opt-${i}" data-index="${i}">${opt}</button>`
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
