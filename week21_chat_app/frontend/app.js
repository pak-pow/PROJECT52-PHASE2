// --- DOM ELEMENTS ---
const connectionStatus = document.getElementById("connection-status");
const statusDot = document.querySelector(".status-dot");
const chatWindow = document.getElementById("chat-window");
const messageInput = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const usernameInput = document.getElementById('username-input');

// --- WEBSOCKET CONNECTION ---
const socket = io("http://127.0.0.1:5000");

socket.on("connect", () => {
  console.log("Connected to server!");
  connectionStatus.textContent = "Online";
  connectionStatus.classList.add("online");
  statusDot.classList.add("online");
});

socket.on("disconnect", () => {
  console.log("Disconnected from server.");
  connectionStatus.textContent = "Offline";
  connectionStatus.classList.remove("online");
  statusDot.classList.remove("online");
});

// --- MESSAGING LOGIC ---

function sendMessage() {
  const text = messageInput.value.trim();
  const user = usernameInput.value.trim() || 'Anonymous';

  if (text === "") return; // Prevent sending empty blank messages

  // Push the text string down the WebSocket tunnel to Python
  socket.send(text);

  socket.emit('chat_message', {
    username: user,
    message: text
  })
  // Clear the input box so you can type the next message
  messageInput.value = "";
}

// Listen for the Send button click
sendBtn.addEventListener("click", sendMessage);

// Listen for the 'Enter' key being pressed inside the input box
messageInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    sendMessage();
  }
});

socket.on('chat_message', (data) => {
  const myCurrentName = usernameInput.value.trim() || 'Anonymous';
  const isMe = (data.username === myCurrentName);

  const messageDiv = document.createElement('div');

  if (isMe) {
    messageDiv.classList.add('message', 'sent');

  } else {
    messageDiv.classList.add('message', 'received');

  }
  messageDiv.innerHTML = `
    <span class="username">${data.username}</span>
    <p>${data.message}</p>
  `;

  chatWindow.appendChild(messageDiv);
  chatWindow.scrollTop = chatWindow.scrollHeight;
});