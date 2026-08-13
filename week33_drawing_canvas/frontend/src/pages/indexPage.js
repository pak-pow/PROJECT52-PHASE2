import { renderNavbar } from "../components/navbar.js";
import { showToast } from "../utils/helpers.js";

document.addEventListener("DOMContentLoaded", () => {
    renderNavbar();

    const createNicknameInput = document.getElementById("create-nickname-input");
    const createRoomBtn = document.getElementById("create-room-btn");

    const joinNicknameInput = document.getElementById("join-nickname-input");
    const joinRoomCodeInput = document.getElementById("join-room-code-input");
    const joinRoomBtn = document.getElementById("join-room-btn");

    // Random default nickname generator
    const randomArtistId = Math.floor(Math.random() * 900 + 100);
    if (createNicknameInput) createNicknameInput.value = `Artist-${randomArtistId}`;
    if (joinNicknameInput) joinNicknameInput.value = `Artist-${randomArtistId}`;

    // Handle Create Room
    createRoomBtn?.addEventListener("click", async () => {
        const nickname = createNicknameInput.value.trim() || `Artist-${randomArtistId}`;
        
        try {
            showToast("Generating room code...", "info");
            const res = await fetch("http://127.0.0.1:5000/api/rooms", {
                method: "POST",
                headers: { "Content-Type": "application/json" }
            });
            
            if (res.ok) {
                const data = await res.json();
                const roomCode = data.room_code;
                showToast(`Room ${roomCode} created! Joining...`, "success");
                setTimeout(() => {
                    window.location.href = `room.html?room=${roomCode}&name=${encodeURIComponent(nickname)}`;
                }, 400);
            } else {
                showToast("Failed to create room.", "error");
            }
        } catch (err) {
            showToast("Backend server offline. Entering DEMO room...", "warning");
            setTimeout(() => {
                window.location.href = `room.html?room=CANVAS-DEMO&name=${encodeURIComponent(nickname)}`;
            }, 600);
        }
    });

    // Handle Join Room
    joinRoomBtn?.addEventListener("click", () => {
        const nickname = joinNicknameInput.value.trim() || `Artist-${randomArtistId}`;
        const roomCode = joinRoomCodeInput.value.trim().toUpperCase();

        if (!roomCode) {
            showToast("Please enter a room code.", "warning");
            return;
        }

        showToast(`Entering room ${roomCode}...`, "info");
        setTimeout(() => {
            window.location.href = `room.html?room=${roomCode}&name=${encodeURIComponent(nickname)}`;
        }, 400);
    });
});
