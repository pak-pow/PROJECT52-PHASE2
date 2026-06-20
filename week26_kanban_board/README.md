# Week 26: Kanban Board (Trello Clone)

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
- **Comprehensive Testing:** An 89-test Pytest suite utilizing a temporary test database to rigorously verify isolated endpoints, validation logic, and cascade deletions.
- **Middleware:** Custom request logger tracking HTTP methods, paths, and response times in the terminal.

### Frontend Features (Upcoming - Day 2)
- Vite + Vanilla JS scaffolding.
- CSS Variables for a dynamic design system.
- HTML5 native Drag and Drop API implementation.
- Real-time DOM updates synchronized with backend state.

## 🗄️ Folder Structure
```text
week26_kanban_board/
│
├── backend/                 # Flask REST API
│   ├── app/                 # Application Factory & Core Logic
│   │   ├── config/          # Settings & CORS config
│   │   ├── middlewares/     # Request Loggers
│   │   ├── models/          # Database Queries (SQLite)
│   │   ├── routes/          # API Endpoints
│   │   ├── services/        # Business Logic & Validation
│   │   └── utils/           # Database Connectors & Helpers
│   ├── data/                # SQLite Database & Schema
│   ├── tests/               # 89 Automated Pytest Suite
│   ├── seed.py              # Idempotent Sample Data Generator
│   ├── run.py               # Server Entrypoint
│   └── requirements.txt     # Python Dependencies
│
└── frontend/                # Vite Vanilla JS UI (Upcoming)
    └── index.html
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
pytest tests/ -v
```

### 3. Start the Frontend (Day 2 WIP)
Open a new terminal and navigate to the frontend folder:
```bash
cd week26_kanban_board/frontend
npm install
npm run dev
```

## 📡 API Endpoints

### Boards
- `GET /api/boards` - List all boards
- `POST /api/boards` - Create a new board
- `GET /api/boards/<id>` - Get a board (includes all columns & cards)
- `PUT /api/boards/<id>` - Update board details
- `DELETE /api/boards/<id>` - Delete board (cascades to columns/cards)

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
