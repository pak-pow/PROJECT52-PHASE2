export class SocketClient {
    /**
     * Socket.io WebSocket Client Wrapper for CanvasSync.
     */
    constructor(serverUrl = "http://127.0.0.1:5000") {
        this.serverUrl = serverUrl;
        this.socket = null;
        this.handlers = {};
    }

    connect() {
        if (typeof io === "undefined") {
            console.error("Socket.io client library not loaded.");
            return;
        }

        this.socket = io(this.serverUrl, {
            transports: ["websocket", "polling"]
        });

        this.socket.on("connect", () => {
            console.log("Connected to CanvasSync WebSocket server with SID:", this.socket.id);
            if (this.handlers.onConnect) this.handlers.onConnect(this.socket.id);
        });

        this.socket.on("room_joined", (data) => {
            if (this.handlers.onRoomJoined) this.handlers.onRoomJoined(data);
        });

        this.socket.on("user_joined", (data) => {
            if (this.handlers.onUserJoined) this.handlers.onUserJoined(data);
        });

        this.socket.on("user_left", (data) => {
            if (this.handlers.onUserLeft) this.handlers.onUserLeft(data);
        });

        this.socket.on("stroke_received", (data) => {
            if (this.handlers.onStrokeReceived) this.handlers.onStrokeReceived(data);
        });

        this.socket.on("canvas_cleared", (data) => {
            if (this.handlers.onCanvasCleared) this.handlers.onCanvasCleared(data);
        });

        this.socket.on("cursor_update", (data) => {
            if (this.handlers.onCursorUpdate) this.handlers.onCursorUpdate(data);
        });

        this.socket.on("chat_received", (data) => {
            if (this.handlers.onChatReceived) this.handlers.onChatReceived(data);
        });

        this.socket.on("reaction_received", (data) => {
            if (this.handlers.onReactionReceived) this.handlers.onReactionReceived(data);
        });

        this.socket.on("error", (data) => {
            if (this.handlers.onError) this.handlers.onError(data);
        });
    }

    joinRoom(roomCode, username) {
        if (this.socket) {
            this.socket.emit("join_room", { room_code: roomCode, username });
        }
    }

    sendStroke(roomCode, strokeData) {
        if (this.socket) {
            this.socket.emit("draw_stroke", { room_code: roomCode, stroke: strokeData });
        }
    }

    sendCursor(roomCode, username, color, x, y) {
        if (this.socket) {
            this.socket.emit("cursor_move", { room_code: roomCode, username, color, x, y });
        }
    }

    sendChatMessage(roomCode, username, message) {
        if (this.socket) {
            this.socket.emit("send_chat", { room_code: roomCode, username, message });
        }
    }

    sendReaction(roomCode, username, emoji) {
        if (this.socket) {
            this.socket.emit("send_reaction", { room_code: roomCode, username, emoji });
        }
    }

    clearCanvas(roomCode) {
        if (this.socket) {
            this.socket.emit("clear_canvas", { room_code: roomCode });
        }
    }

    on(event, handler) {
        this.handlers[event] = handler;
    }
}
