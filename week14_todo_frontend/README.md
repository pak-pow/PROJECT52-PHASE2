# 🖥️ Week 14: Premium Todo App Frontend

Welcome to Week 14 of **PROJECT52**! This project serves as the client-side user interface for the Full-Stack Todo application. It connects directly to the Week 13 Python Flask REST API to perform complete CRUD operations using asynchronous JavaScript, wrapped in a premium, modern UI.

## 🚀 Core Features

- **Full CRUD Integration:** Communicates with the backend to Create, Read, Update, and Delete tasks in real-time.
- **Asynchronous Fetch API:** Utilizes modern `async/await` JavaScript to handle network requests without freezing the UI.
- **Client-Side Filtering:** Features state management to filter tasks by "All", "Active", and "Completed" instantly in the DOM.
- **Dynamic Empty States:** JavaScript logic intercepts empty arrays to provide contextual, friendly UI messages instead of blank screens.

## 🎨 Premium UI/UX Design

- **Glassmorphism:** Utilizes CSS `backdrop-filter` to create a frosted glass container over a dynamic, animated gradient background.
- **Micro-interactions:** Features smooth `slideIn` keyframe animations for DOM rendering and tactile hover transformations for interactive elements.
- **Modern Typography:** Styled with the highly legible `Inter` font family and gradient text clipping.

## 🛠️ Tech Stack

- **Structure:** HTML5
- **Styling:** CSS3 (Flexbox, Glassmorphism, Keyframes)
- **Logic:** Vanilla JavaScript (ES6+)
- **Network:** Fetch API

---

## 💻 How to Run Locally

**⚠️ CRITICAL PREREQUISITE:** Because this is a decoupled Full-Stack application, the Frontend **will not work** unless the Week 13 Python Backend is actively running.

**1. Boot the Backend Database:**
Open a terminal, navigate to the API directory, and start the Flask server.

```bash
cd VSCODE_PROJECT52/week13_todo_api
python app.py
```

_(Ensure it is running on `http://127.0.0.1:5000`)_

**2. Boot the Frontend UI:**
Open a separate terminal or use your code editor to serve the frontend files.
If using VS Code, simply right-click `index.html` and select **"Open with Live Server"**.

**3. Test the Connection:**
If the bridge is successful, the UI will immediately populate with the data stored in the backend's `todos.json` file.
