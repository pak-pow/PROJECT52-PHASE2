import { escapeHtml } from "../utils/helpers.js";

export function renderParticipantList(containerElement, usersList = []) {
    if (!containerElement) return;

    const listHtml = usersList.map(user => `
        <div class="participant-item">
            <span class="user-avatar-dot" style="background-color: ${user.color || '#3b82f6'};"></span>
            <span class="user-name">${escapeHtml(user.username)}</span>
        </div>
    `).join("");

    containerElement.innerHTML = `
        <div class="participant-panel">
            <div class="participant-header">
                <span>👥 Room Artists (${usersList.length})</span>
            </div>
            <div class="participant-list">
                ${listHtml || '<div class="empty-list">No artists in room</div>'}
            </div>
        </div>
    `;
}
