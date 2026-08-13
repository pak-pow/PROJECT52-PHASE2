import { escapeHtml } from "../utils/helpers.js";

export function renderChatBox(containerElement, onSendMessage, onSendReaction) {
    if (!containerElement) return;

    const REACTIONS = ["❤️", "🎉", "🔥", "👏", "💡"];
    const reactionsHtml = REACTIONS.map(emoji => `
        <button class="reaction-btn" data-emoji="${emoji}">${emoji}</button>
    `).join("");

    containerElement.innerHTML = `
        <div class="chat-panel">
            <div class="chat-header">
                <span>💬 Room Chat</span>
                <button id="toggle-chat-btn" class="chat-toggle-btn">▼</button>
            </div>
            
            <div id="chat-body" class="chat-body">
                <div class="chat-messages" id="chat-messages">
                    <div class="chat-system-msg">Welcome to room chat! Say hi to fellow artists.</div>
                </div>

                <!-- Reaction Emoji Bar -->
                <div class="reaction-bar">
                    ${reactionsHtml}
                </div>

                <div class="chat-input-row">
                    <input type="text" id="chat-input" class="chat-input" placeholder="Type a message..." maxlength="150">
                    <button id="send-chat-btn" class="btn-primary" style="padding: 0.4rem 0.75rem; font-size: 0.8rem;">Send</button>
                </div>
            </div>
        </div>
    `;

    const chatBody = document.getElementById("chat-body");
    const toggleBtn = document.getElementById("toggle-chat-btn");
    let isCollapsed = false;

    toggleBtn?.addEventListener("click", () => {
        isCollapsed = !isCollapsed;
        chatBody.style.display = isCollapsed ? "none" : "flex";
        toggleBtn.textContent = isCollapsed ? "▲" : "▼";
    });

    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-chat-btn");

    const doSend = () => {
        const text = chatInput.value.trim();
        if (text && onSendMessage) {
            onSendMessage(text);
            chatInput.value = "";
        }
    };

    sendBtn?.addEventListener("click", doSend);
    chatInput?.addEventListener("keypress", (e) => {
        if (e.key === "Enter") doSend();
    });

    containerElement.querySelectorAll(".reaction-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const emoji = btn.getAttribute("data-emoji");
            if (emoji && onSendReaction) onSendReaction(emoji);
        });
    });
}

export function appendChatMessage(username, message) {
    const messagesContainer = document.getElementById("chat-messages");
    if (!messagesContainer) return;

    const msgEl = document.createElement("div");
    msgEl.className = "chat-msg-item";
    msgEl.innerHTML = `
        <strong class="chat-sender">${escapeHtml(username)}:</strong>
        <span class="chat-text">${escapeHtml(message)}</span>
    `;
    messagesContainer.appendChild(msgEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

export function triggerFloatingEmoji(username, emoji) {
    const mainWorkspace = document.getElementById("workspace-main");
    if (!mainWorkspace) return;

    const floatEl = document.createElement("div");
    floatEl.className = "floating-emoji-badge";
    floatEl.innerHTML = `<span>${emoji}</span> <small>${escapeHtml(username)}</small>`;

    // Random horizontal starting position
    const randomLeft = Math.floor(Math.random() * 60 + 20);
    floatEl.style.left = `${randomLeft}%`;
    floatEl.style.bottom = "80px";

    mainWorkspace.appendChild(floatEl);

    setTimeout(() => {
        floatEl.remove();
    }, 2500);
}
