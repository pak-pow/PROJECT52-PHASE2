// --- DOM ELEMENTS ---
const joinScreen = document.getElementById("join-screen");
const joinUsernameInput = document.getElementById("join-username-input");
const joinBtn = document.getElementById("join-btn");

const chatContainer = document.getElementById("chat-container");
const connectionStatus = document.getElementById("connection-status");
const statusDot = document.querySelector(".status-dot");
const displayUsername = document.getElementById("display-username");
const chatWindow = document.getElementById("chat-window");
const messageInput = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const typingIndicator = document.getElementById("typing-indicator");

const joinRoomSelect = document.getElementById("join-room-select");
const displayRoom = document.getElementById("display-room");

let myRoom = "";
let socket;
let myUsername = "";
let typingTimer;

function startChat() {
  const name = joinUsernameInput.value.trim();
  if (name === "") {
    alert("Please enter a name to join the chat.");
    return;
  }

  myUsername = name;
  myRoom = joinRoomSelect.value;

  joinScreen.classList.add("hidden");
  chatContainer.classList.remove("hidden");
  displayUsername.textContent = myUsername;
  displayRoom.textContent = `[${myRoom}]`;

  socket = io("http://127.0.0.1:5000");
  initializeSocketListeners();
}

joinBtn.addEventListener("click", startChat);
joinUsernameInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") startChat();
});

function initializeSocketListeners() {
  socket.on("connect", () => {
    connectionStatus.textContent = "Online";
    connectionStatus.classList.add("online");
    statusDot.classList.add("online");

    socket.emit("user_join", { username: myUsername, room: myRoom });
  });

  socket.on("disconnect", () => {
    connectionStatus.textContent = "Offline";
    connectionStatus.classList.remove("online");
    statusDot.classList.remove("online");
  });

  socket.on("system_message", (msg) => {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", "system");
    messageDiv.innerHTML = `<p>${msg}</p>`;
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  });

  socket.on("chat_message", (data) => {
    const isMe = data.username === myUsername;
    const messageDiv = document.createElement("div");

    if (isMe) messageDiv.classList.add("message", "sent");
    else messageDiv.classList.add("message", "received");

    messageDiv.innerHTML = `
            <span class="username">${data.username}</span>
            <p>${data.message}</p>
            <span class="timestamp">${data.timestamp}</span>
        `;

    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  });

  socket.on("typing", (data) => {
    if (data.isTyping) {
      typingIndicator.textContent = `${data.username} is typing...`;
      clearTimeout(typingTimer);
      typingTimer = setTimeout(() => {
        typingIndicator.textContent = "";
      }, 2000);
    } else {
      typingIndicator.textContent = "";
    }
  });

  function sendMessage() {
    const text = messageInput.value.trim();
    if (text === "") return;

    const timeString = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    socket.emit("chat_message", {
      username: myUsername,
      message: text,
      timestamp: timeString,
      room: myRoom,
    });

    messageInput.value = "";
    socket.emit("typing", {
      username: myUsername,
      isTyping: false,
      room: myRoom,
    });
  }

  sendBtn.addEventListener("click", sendMessage);
  messageInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  messageInput.addEventListener("input", () => {
    socket.emit("typing", {
      username: myUsername,
      isTyping: true,
      room: myRoom,
    });
  });
}
