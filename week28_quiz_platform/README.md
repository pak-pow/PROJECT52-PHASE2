# Week 28: Quiz Platform with Leaderboards

A modern, responsive, full-stack trivia platform featuring real-time interactive quizzes, SVG circular countdown timers, correct/incorrect answer breakdowns, and competitive leaderboards.

---

## 📁 Project Structure

```
week28_quiz_platform/
├── backend/
│   ├── app/
│   │   ├── config/       # App settings and CORS origins configuration
│   │   ├── models/       # SQLite database model query helper functions
│   │   ├── routes/       # API endpoints (Blueprints)
│   │   ├── services/     # Business logic, validation, and grading
│   │   └── db.py         # DB connection and init routines
│   ├── data/
│   │   ├── schema.sql    # Clean database schema table layout
│   │   └── seed.py       # Standalone dynamic data seeder
│   ├── tests/            # pytest suite for route and validation checks
│   ├── requirements.txt  # Python package requirements
│   ├── run.py            # Flask development runner
│   └── wsgi.py           # Production Waitress WSGI runner
└── frontend/
    ├── public/
    │   └── index.html    # Minimalist shell interface (injects templates on boot)
    └── src/
        ├── api/          # async fetch requests
        ├── assets/       # Split modular stylesheet design tokens
        ├── components/   # Reusable components (modals)
        ├── pages/        # View HTML templates and rendering engines
        ├── utils/        # SVG countdown timer and helper scripts
        └── main.js       # App boots and registers window key controllers
```

---

## 🚀 Backend Quickstart

### 1. Requirements Installation
Ensure you are inside the `backend/` directory, then create a virtual environment and install packages:
```bash
pip install -r requirements.txt
```

### 2. Populate the Database
To create tables and seed the database with the sample quizzes:
```bash
# Safe seeding (ignores existing records to prevent duplicates)
python data/seed.py

# Complete reset (wipes all existing data and seeds fresh)
python data/seed.py --reset
```
*Seeds 4 quizzes (Web Dev, Python, JavaScript, Databases) with 5 questions each.*

### 3. Run the Server
* **Development Server** (runs with hot-reloading active):
  ```bash
  python run.py
  ```
* **Production WSGI Server** (hosted via Waitress on Windows/Linux):
  ```bash
  python wsgi.py
  ```

---

## 🧪 Testing

Run backend unit tests verifying endpoint contracts, CORS headers, health checks, array boundaries, and input payload validation:
```bash
# Navigate to backend/ directory
pytest -v
```

---

## 💻 Frontend Quickstart

1. Serve the `frontend/` directory using any local development static server. 
2. We recommend using the VS Code **Live Server** extension (hosts at `http://127.0.0.1:5500`).
3. Open `http://127.0.0.1:5500/week28_quiz_platform/frontend/public/index.html` in your browser.

*Note: No bundler or package installation is required for the frontend. It runs natively in modern browsers using ES Modules (`type="module"`).*

---

## ⌨️ Accessibility Keyboard Shortcuts
When inside an active quiz, you can navigate entirely using your keyboard:
* **`1` to `4`**: Highlight option answers 1 through 4.
* **`Enter`**: Go to the next question / Submit answers (when Next button becomes active).
