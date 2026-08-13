import { renderNavbar } from "../components/navbar.js";
import { renderToolbar } from "../components/toolbar.js";
import { renderParticipantList } from "../components/participantList.js";
import { renderChatBox, appendChatMessage, triggerFloatingEmoji } from "../components/chatBox.js";
import { CanvasEngine } from "../engine/canvasEngine.js";
import { CursorTracker } from "../engine/cursorTracker.js";
import { HistoryManager } from "../engine/historyManager.js";
import { SocketClient } from "../api/socketClient.js";
import { getQueryParam, showToast, exportCanvasToPng } from "../utils/helpers.js";

document.addEventListener("DOMContentLoaded", () => {
    const roomCode = (getQueryParam("room") || "CANVAS-DEMO").toUpperCase();
    const username = getQueryParam("name") || "Artist-" + Math.floor(Math.random() * 1000);
    renderNavbar(roomCode);

    const canvasElement = document.getElementById("drawing-canvas");
    const cursorContainer = document.getElementById("cursor-container");
    const participantContainer = document.getElementById("participant-container");
    const chatContainer = document.getElementById("chat-container");

    if (!canvasElement) return;

    // 1. Initialize Real-Time WebSocket Client & History Manager
    const socketClient = new SocketClient("http://127.0.0.1:5000");
    const cursorTracker = new CursorTracker(cursorContainer);
    const historyManager = new HistoryManager(30);

    let myAvatarColor = "#3b82f6";

    // Save initial blank canvas state
    setTimeout(() => {
        historyManager.saveState(canvasEngine.ctx, canvasElement);
    }, 200);

    // 2. Initialize Canvas Engine with stroke emit callback
    const canvasEngine = new CanvasEngine(canvasElement, (strokeData) => {
        socketClient.sendStroke(roomCode, strokeData);
        historyManager.saveState(canvasEngine.ctx, canvasElement);
    });

    // 3. Render Floating Toolbar Controls
    renderToolbar(
        (tool) => {
            canvasEngine.setTool(tool);
            showToast(`Tool: ${tool.toUpperCase()}`, "info");
        },
        (color) => canvasEngine.setColor(color),
        (size) => canvasEngine.setSize(size),
        () => {
            socketClient.clearCanvas(roomCode);
        },
        () => {
            const success = historyManager.undo(canvasEngine.ctx, canvasElement);
            if (success) showToast("Undo action ↩️", "info");
        },
        () => {
            const success = historyManager.redo(canvasEngine.ctx, canvasElement);
            if (success) showToast("Redo action ↪️", "info");
        },
        () => {
            exportCanvasToPng(canvasElement, roomCode);
        }
    );

    // 4. Render In-Room Chat Box
    renderChatBox(
        chatContainer,
        (msgText) => {
            socketClient.sendChatMessage(roomCode, username, msgText);
        },
        (emoji) => {
            socketClient.sendReaction(roomCode, username, emoji);
        }
    );

    // Keyboard Shortcuts (Ctrl+Z / Ctrl+Y)
    window.addEventListener("keydown", (e) => {
        if (e.ctrlKey && e.key.toLowerCase() === "z") {
            e.preventDefault();
            const success = historyManager.undo(canvasEngine.ctx, canvasElement);
            if (success) showToast("Undo action ↩️", "info");
        } else if (e.ctrlKey && e.key.toLowerCase() === "y") {
            e.preventDefault();
            const success = historyManager.redo(canvasEngine.ctx, canvasElement);
            if (success) showToast("Redo action ↪️", "info");
        }
    });

    // 5. WebSocket Event Handlers
    socketClient.on("onConnect", () => {
        socketClient.joinRoom(roomCode, username);
    });

    socketClient.on("onRoomJoined", (data) => {
        if (data.user) myAvatarColor = data.user.color || "#3b82f6";
        showToast(`Joined room ${data.room_code} as ${data.user?.username || username}`, "success");

        renderParticipantList(participantContainer, data.users_list || []);

        // Replay stroke history for late joiners
        if (data.strokes_history && Array.isArray(data.strokes_history)) {
            data.strokes_history.forEach(stroke => {
                canvasEngine.renderExternalStroke(stroke);
            });
        }
    });

    socketClient.on("onUserJoined", (data) => {
        showToast(`${data.user?.username || 'An artist'} joined the room! 👋`, "info");
        renderParticipantList(participantContainer, data.users_list || []);
    });

    socketClient.on("onUserLeft", (data) => {
        if (data.user) {
            showToast(`${data.user.username} left the room.`, "warning");
            cursorTracker.removeCursor(data.user.sid);
        }
        renderParticipantList(participantContainer, data.users_list || []);
    });

    socketClient.on("onStrokeReceived", (strokeData) => {
        canvasEngine.renderExternalStroke(strokeData);
    });

    socketClient.on("onCanvasCleared", () => {
        canvasEngine.clear();
        showToast("Canvas cleared by room member 🗑️", "info");
    });

    socketClient.on("onCursorUpdate", (cursorData) => {
        cursorTracker.updateRemoteCursor(cursorData);
    });

    socketClient.on("onChatReceived", (chatData) => {
        appendChatMessage(chatData.username, chatData.message);
    });

    socketClient.on("onReactionReceived", (reactionData) => {
        triggerFloatingEmoji(reactionData.username, reactionData.emoji);
    });

    // 6. Throttled Mousemove Cursor Broadcast (30fps)
    let lastCursorEmit = 0;
    canvasElement.addEventListener("mousemove", (e) => {
        const now = Date.now();
        if (now - lastCursorEmit > 33) {
            lastCursorEmit = now;
            const rect = canvasElement.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            socketClient.sendCursor(roomCode, username, myAvatarColor, x, y);
        }
    });

    // Connect to WebSocket server
    socketClient.connect();
});
