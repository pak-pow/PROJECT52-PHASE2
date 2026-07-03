# Week 26: Kanban Board (Trello Clone)

**Category:** Full Stack | **Status:** Completed

A full-stack, drag-and-drop Kanban board application featuring persistent state management, deeply nested relational data, and smooth UI interactions.

## 🚀 Project Overview
This project simulates a Trello-style workflow where users can create multiple Boards, add Columns to those Boards, and manage Tasks (Cards) within those Columns. It demonstrates complex data relationships, API-driven state management, and HTML5 Drag-and-Drop capabilities.

## 🏗️ Architecture

The project strictly follows a decoupled Client-Server architecture:

- **Backend (`/backend`)**: A RESTful Python API powered by Flask and SQLite.
- **Frontend (`/frontend`)**: A modern Vanilla JavaScript application bundled with Vite.

### Backend Features (Complete)
- **Strict Relational Integrity:** SQLite schema enforcing `ON DELETE CASCADE`. Deleting a board automatically purges all child columns and cards.
- **Service Layer Pattern:** Dedicated services to validate inputs, intercept bad requests, and cleanly separate database logic from HTTP routing.
- **Hydrated Responses:** Requesting a board automatically fetches and nests all its associated columns and cards in a single, clean JSON payload.
- **Drag-and-Drop Endpoints:** Dedicated `PATCH /reorder` and `PATCH /move` endpoints designed specifically to handle complex positional shifts when a user drags a card.
- **User Authentication & Multi-Tenant Isolation:** Database-backed user sessions (`/api/auth`) secured using `Authorization: Bearer` headers to prevent cross-site cookies issues. Queries are locked down at the resource owner level.
- **Comprehensive Testing:** A 113-test Pytest suite utilizing a temporary test database to verify authentication routes, user isolation boundaries, validation logic, and cascade deletions.
- **Middleware:** Custom request logger tracking HTTP methods, paths, and response times in the terminal.

### Frontend Features (Complete)
- **Vite + Vanilla JS Architecture:** Structured Single Page Application (SPA) with routing, modular pages (auth, dashboard, board), and component controllers.
- **CSS Variables Design System:** Custom dark-theme variables for styling flexibility, premium animations, and color picker support.
- **Native HTML5 Drag and Drop:** Drag-and-drop support for boards reordering, columns reordering, and cards movement across lists with smooth optimistic DOM updates.
- **State Persistence & Security Guards:** Session authorization headers persistence in `localStorage`, automatic 401 interceptors, and client-side page routing guards.
- **Micro-Animations & Visual Polish:** Custom non-blocking toast notifications (success/error feedback), unified height controls, and dynamic accent color theme resets.

## 🗄️ Folder Structure
```text
week26_kanban_board/
│
├── backend/                 # Flask REST API
│   ├── app/                 # Application Factory & Core Logic
│   │   ├── config/          # Settings & CORS config
│   │   ├── middlewares/     # Request Loggers & Auth Middleware
│   │   ├── models/          # Database Queries (User, Board, Column, Card)
│   │   ├── routes/          # API Endpoints (Auth, Boards, Columns, Cards)
│   │   ├── services/        # Business Logic & Validation (Board, Card)
│   │   └── utils/           # Database Connectors & Helpers
│   ├── data/                # SQLite Database & Schema
│   ├── tests/               # 113 Automated Pytest Suite (Auth, Isolation, CRUD)
│   ├── run.py               # Server Entrypoint
│   ├── seed.py              # Sample Data Generator
│   └── requirements.txt     # Python Dependencies
│
└── frontend/                # Vite Vanilla JS UI
    ├── index.html           # Main SPA Entry
    ├── package.json         # Node Scripts & Vite Configuration
    └── src/
        ├── api/             # API Client Interface (Token persistence)
        ├── assets/          # Base Styles, Layout, Components, and variables.css
        ├── components/      # UI Templates (boardCard, card, column)
        ├── pages/           # Pages (auth, dashboard, board)
        ├── utils/           # Utilities (dom helpers, drag-and-drop handlers)
        └── main.js          # App Bootstrapper & Router Guard
```

## 🛠️ How to Run

### 1. Start the Backend
Open a terminal and navigate to the backend folder:
```bash
cd week26_kanban_board/backend
python -m venv .venv
source .venv/Scripts/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# (Optional) Seed the database with sample data
python seed.py

# Start the server
python run.py
```
The API will run at `http://127.0.0.1:5000`.

### 2. Run the Tests
To verify the backend integrity, run the automated test suite:
```bash
pytest -v
```

### 3. Start the Frontend
Open a new terminal and navigate to the frontend folder:
```bash
cd week26_kanban_board/frontend
npm install
npm run dev
```
The client app will run at `http://localhost:5173`.

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Create a new user account & auto-login
- `POST /api/auth/login` - Verify credentials & generate session token
- `POST /api/auth/logout` - Invalidate active session token
- `GET /api/auth/me` - Fetch authenticated user details

### Boards
- `GET /api/boards` - List all boards for the logged-in user
- `POST /api/boards` - Create a new board
- `GET /api/boards/<id>` - Get a board (includes all columns & cards)
- `PUT /api/boards/<id>` - Update board details
- `DELETE /api/boards/<id>` - Delete board (cascades to columns/cards)
- `PATCH /api/boards/reorder` - Bulk update board positions

### Columns
- `GET /api/boards/<id>/columns` - List columns for a board
- `POST /api/boards/<id>/columns` - Create a column on a board
- `PUT /api/columns/<id>` - Rename a column
- `DELETE /api/columns/<id>` - Delete a column (cascades to cards)
- `PATCH /api/boards/<id>/columns/reorder` - Bulk update column positions

### Cards
- `GET /api/columns/<id>/cards` - List cards in a column
- `GET /api/cards/<id>` - Get single card details
- `POST /api/columns/<id>/cards` - Create a card
- `PUT /api/cards/<id>` - Update card text/description
- `DELETE /api/cards/<id>` - Delete a card
- `PATCH /api/columns/<id>/cards/reorder` - Reorder cards within the *same* column
- `PATCH /api/cards/<id>/move` - Move a card to a *different* column
