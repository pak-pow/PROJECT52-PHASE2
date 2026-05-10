# 📝 Full-Stack Markdown Notes

A lightweight, local-first Markdown note-taking application built with Vanilla JavaScript, HTML/CSS, and a Python/Flask REST API. 

Developed as **Week 19** of [Project 52] — a year-long challenge to build one software project every week.

## ✨ Features
* **Real-Time Parsing:** Live compilation of GitHub Flavored Markdown (GFM) into HTML using `marked.js`.
* **Full CRUD API:** Secure Python backend handling Creation, Reading, Updating (Renaming), and Deletion of `.md` files via RESTful routes.
* **Security First:** Hardened endpoints utilizing `secure_filename` to prevent Path Traversal attacks.
* **Advanced UI/UX:** * Asynchronous Toast Notification system.
  * Live Word and Character count telemetry.
  * Client-side search and filtering capabilities.
  * Native dark-mode scrollbars and CSS Flexbox split-pane architecture.
* **Data Loss Prevention:** Global state management intercepts navigation if unsaved changes are detected.

## 🛠️ Technology Stack
* **Frontend:** HTML5, CSS3 (Variables, Flexbox), Vanilla JavaScript (ES6+ Asynchronous Fetch API).
* **Backend:** Python 3, Flask (RESTful Routing, CORS Management), `werkzeug` (Security).
* **Parsing Engine:** `marked.js` (via CDN).

## 🚀 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pak-pow/PROJECT52-PHASE2
   cd /PROJECT52-PHASE2/week19_markdown_notes
    ```

2. **Setup the Python Backend:**
Ensure you have Python installed, then install the required dependencies:
    ```bash
    pip install flask flask-cors werkzeug
    ```

3. **Boot the API Server:**
Navigate to the backend directory and run the server:
    ```bash
    cd backend
    python app.py
    ```

    *The server will start on `http://127.0.0.1:5000*`

4. **Launch the Frontend:**
Open `frontend/index.html` in any modern web browser (or use VS Code Live Server).

