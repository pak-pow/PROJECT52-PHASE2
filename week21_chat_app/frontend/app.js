// --- DOM ELEMENTS ---
const connectionStatus = document.getElementById("connection-status");
const statusDot = document.querySelector(".status-dot");
const chatWindow = document.getElementById("chat-window");
const messageInput = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");

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
  if (text === "") return; // Prevent sending empty blank messages

  // Push the text string down the WebSocket tunnel to Python
  socket.send(text);

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

// This listens for Python broadcasting a message back to us
socket.on("message", (msg) => {
  // Create a new div for the message
  const messageDiv = document.createElement("div");

  // For today, we will style all incoming messages as "received"
  messageDiv.classList.add("message", "received");

  // Build the HTML structure
  messageDiv.innerHTML = `
        <span class="username">Anonymous</span>
        <p>${msg}</p>
    `;

  // Append it to the bottom of our chat window
  chatWindow.appendChild(messageDiv);

  // Auto-scroll the chat window to the very bottom
  chatWindow.scrollTop = chatWindow.scrollHeight;
});
