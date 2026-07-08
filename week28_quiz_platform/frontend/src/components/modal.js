/* ── HTML Template ───────────────────────────────────────────── */
export const MODAL_HTML = `
  <div id="modal-username" class="modal-overlay hidden">
    <div class="modal-card">
      <h2 class="modal-title">Enter Your Name</h2>
      <p class="modal-sub">Your name will appear on the leaderboard.</p>
      <input
        type="text"
        id="input-username"
        class="modal-input"
        placeholder="e.g. vincent"
        maxlength="24"
        autocomplete="off"
      />
      <div class="modal-actions">
        <button id="btn-submit-username" class="btn-primary">Submit Answers &#8594;</button>
      </div>
    </div>
  </div>
`;

/* ── Functions ───────────────────────────────────────────────── */
export function openModal() {

  const modal = document.getElementById("modal-username");
  const input = document.getElementById("input-username");
  modal.classList.remove("hidden");
  input.value = "";
  input.focus();
}

export function closeModal() {
  document.getElementById("modal-username").classList.add("hidden");
}
