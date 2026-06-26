# Week 27: Portfolio v2 with Backend

**Project 52 — Phase 2 | Week 27**  
**Category:** Full Stack  
**Skills:** Flask, SQLite, Vanilla JS, AJAX, Admin Dashboard  
**Estimated Time:** 7 hours  
**Status:** In Progress

---

## Overview

An upgraded version of the static Week 1 portfolio, now powered by a Flask backend and SQLite database.

| Feature | v1 (Week 1) | v2 (This Week) |
|---|---|---|
| Stack | HTML + CSS | Flask + SQLite + JS |
| Contact | `mailto:` link | Real form → DB |
| Projects | Hard-coded cards | DB-driven via admin |
| Admin Panel | None | Full CRUD dashboard |
| Font | Courier New | Outfit + Courier New |
| Design | Basic dark | Glassmorphism + glow |

---

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python run.py
```

The server runs on **http://localhost:5000**. The database is auto-created on first run.

### Frontend

Open `frontend/index.html` with VS Code **Live Server** (port 5500) or any static file server.

> Make sure the backend is running first, or the projects grid and contact form won't work.

---

## Admin Access

Navigate to `frontend/admin.html` (linked in the footer as "Admin").

| Field | Default |
|---|---|
| Username | `admin` |
| Password | `admin123` |

> Change credentials by setting environment variables `ADMIN_USERNAME` and `ADMIN_PASSWORD`.

---

## API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/health` | None | Health check |
| GET | `/api/projects` | None | List all projects |
| POST | `/api/contact` | None | Submit contact form |
| POST | `/api/admin/login` | None | Admin login → token |
| POST | `/api/admin/logout` | ✓ Bearer | Revoke token |
| GET | `/api/admin/messages` | ✓ Bearer | List all messages |
| PATCH | `/api/admin/messages/<id>/read` | ✓ Bearer | Toggle read status |
| DELETE | `/api/admin/messages/<id>` | ✓ Bearer | Delete message |
| POST | `/api/projects` | ✓ Bearer | Create project |
| PUT | `/api/projects/<id>` | ✓ Bearer | Update project |
| DELETE | `/api/projects/<id>` | ✓ Bearer | Delete project |

---

## Running Tests

```bash
cd backend
python -m pytest -v
```

---

## Project Structure

```
week27_portfolio_v2/
├── backend/
│   ├── app.py              # Flask app factory
│   ├── config.py           # Configuration
│   ├── requirements.txt
│   ├── data/
│   │   └── schema.sql      # DB schema + seed data
│   ├── app/
│   │   ├── db.py
│   │   ├── middlewares/
│   │   │   └── admin_middleware.py
│   │   └── routes/
│   │       ├── contact_routes.py
│   │       ├── projects_routes.py
│   │       └── admin_routes.py
│   └── tests/
│       ├── conftest.py
│       ├── test_contact_routes.py
│       ├── test_projects_routes.py
│       └── test_admin_routes.py
└── frontend/
    ├── index.html          # Home page
    ├── about.html          # About page
    ├── admin.html          # Admin dashboard
    └── src/
        ├── style.css       # Design system
        ├── api.js          # API client
        ├── contact.js      # Form + projects renderer
        └── admin.js        # Admin panel controller
```
