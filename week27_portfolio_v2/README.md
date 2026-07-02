# Week 27: Portfolio v2 with Backend

**Project 52 — Phase 2 | Week 27**  
**Category:** Full Stack  
**Skills:** Flask, SQLite, Vanilla JS, AJAX, Admin Dashboard, Hashed Passwords, Session Expiration, Stacking Toasts, Project Reordering  
**Estimated Time:** 7 hours  
**Status:** Complete

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

> **Security Note**: All passwords are stored and verified securely using `werkzeug.security` cryptographic hashes. Active admin sessions expire after **2 hours** of inactivity. Override credentials by setting environment variables `ADMIN_USERNAME`, `ADMIN_PASSWORD`, or `ADMIN_PASSWORD_HASH`.

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
| POST | `/api/projects/<id>/reorder` | ✓ Bearer | Swap sort order index |
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
    ├── assets/             # Static documents
    │   └── vincent_aguirre_cv.pdf
    └── src/
        ├── style.css       # Design system
        ├── api.js          # API client
        ├── contact.js      # Form + projects renderer
        └── admin.js        # Admin panel controller
```

---

## Weekly Sprint Enhancements

During this sprint, we implemented a series of progressive polishes:
- **Day 2 (Spotlight & Filtering)**: Dynamic top 6 tech tags extractor, featured project showcase, live filters, staggered entrance card transitions, and a local CV downloader.
- **Day 3 (Analytics & Custom Modals)**: Dashboard stats counters with sequential loading animations, and promise-based custom glassmorphic modals replacing standard browser `confirm()` alerts.
- **Day 4 (Security & Search)**: Safe password verification using Werkzeug hashes, 2-hour login session expiration checks in middleware, and a live search and read/unread filtering panel in the admin inbox.
- **Day 5 (Reordering & Validation)**: Live reorder swap (`/reorder`) buttons (▲ / ▼) in the admin dashboard, and glowing live form validity feedback (green for valid, red for invalid).
- **Day 6 (Toast Queueing & Project Search)**: Fixed stacking notification toast queue (bottom-right) with click-dismiss controls, and added real-time project title and status filters to the admin panel.
