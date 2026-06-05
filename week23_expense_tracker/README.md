# 📊 Expense Analytics Dashboard (Project 52 - Week 23)

A full-stack, enterprise-grade financial dashboard built to track, visualize, and export personal expenses. Built with a focus on strict architectural patterns, robust security, and high-performance UI/UX.

![Day7.1](../../PROJECT52/Picture/week23/day7.1.png)
![Day7.2](../../PROJECT52/Picture/week23/day7.2.png)

## 🚀 Features
* **JWT Authentication:** Secure user registration and login flows with hashed passwords and token-based session management.
* **Real-Time Visual Analytics:** Interactive Doughnut charts powered by `Chart.js` that update instantly upon data mutation.
* **Dynamic Filtering:** Query the database in real-time by date ranges and auto-learned custom categories.
* **Client-Side Localization:** Native `Intl.NumberFormat` integration supporting 10 global fiat currencies with persistent state caching.
* **Data Portability:** Instantly export filtered data views to a clean CSV format.
* **Premium UI/UX:** Responsive CSS Grid layout, strict form debouncing to prevent double-posting, and a persistent Dark Mode toggle.

## 🛠️ Tech Stack
* **Backend:** Python, Flask, SQLite3, Werkzeug (Security), Flask-JWT-Extended
* **Frontend:** Vanilla JavaScript (ES6 Modules), HTML5, Custom CSS3 (No Frameworks)
* **Libraries:** Chart.js

## 🏗️ Architectural Highlights
* **MVC Pattern:** Strict separation of Database Models, API Routes, and Business Logic.
* **Single Responsibility Principle:** Monolithic frontend scripts were decoupled into dedicated modules (`login.js`, `currency.js`, `theme.js`).
* **Performance:** Network waterfall optimization using `Promise.all()` for simultaneous data fetching. Canvas lifecycle management to prevent memory leaks during re-renders.

## ⚙️ Local Installation
1. **Clone the repo:** `git clone https://github.com/yourusername/expense-tracker.git`
2. **Setup Python Environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/Scripts/activate  # (Windows: venv\Scripts\activate)
   pip install -r requirements.txt
   ```
3. **Initialize Database:** `python seed.py`
4. **Run Server:** `python run.py`
5. **Run Frontend:** Open `frontend/public/login.html` via Live Server.
