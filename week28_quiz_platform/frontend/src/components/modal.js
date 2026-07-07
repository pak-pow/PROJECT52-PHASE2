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
