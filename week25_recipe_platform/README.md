# 🍽️ Week 25 — Recipe Platform

**Category:** Full Stack | **Status:** Completed

A full-stack recipe management application. Users can **add**, **edit**, **browse**, and **delete** recipes with optional photo uploads. Built as Week 25 of the Project 52 Phase 2 challenge.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, Flask 3.0, SQLite |
| Frontend | Vanilla JS (ES Modules), CSS Custom Properties, Google Fonts (Inter) |
| Testing | pytest |

---

## Features

- 📋 **Browse recipes** in a responsive card grid
- ➕ **Add recipes** via modal form with optional photo upload (PNG, JPG, JPEG, WEBP — max 5 MB)
- ✏️ **Edit recipes** — click Edit on any card to update fields or replace the photo
- 🗑️ **Delete recipes** — removes card and associated image file from disk
- 📄 **Pagination** — 12 recipes per page with Prev/Next controls
- 🔔 **Toast notifications** — non-blocking success/error feedback
- 🔍 **Accordion view** — expand any card to read full ingredients and instructions
- 🖼️ **Image fallback** — broken images gracefully show a placeholder

---

## Project Structure

```
week25_recipe_platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py         # App factory, CORS config, teardown
│   │   ├── config/             # (placeholder)
│   │   ├── middlewares/        # (placeholder)
│   │   ├── models/
│   │   │   └── recipe_model.py # SQL data-access layer (CRUD + pagination)
│   │   ├── routes/
│   │   │   └── recipe_routes.py# Blueprint: all HTTP endpoints
│   │   ├── services/
│   │   │   └── recipe_service.py# Validation + file extension check
│   │   └── utils/
│   │       └── db.py           # SQLite connection + teardown
│   ├── data/
│   │   ├── schema.sql          # CREATE TABLE recipes
│   │   └── database.db         # SQLite database (runtime)
│   ├── tests/
│   │   └── test_recipe_service.py # pytest unit tests
│   ├── uploads/                # Uploaded recipe images (runtime)
│   ├── run.py                  # Dev server entrypoint
│   ├── seed.py                 # One-shot data seeder (idempotent)
│   └── requirements.txt
│
└── frontend/
    ├── public/
    │   └── index.html          # Single-page HTML shell
    └── src/
        ├── config.js           # API base URL (single source of truth)
        ├── main.js             # App controller (grid, modals, pagination, toast)
        ├── api/
        │   └── recipe_api.js   # Fetch wrappers for all API calls
        └── assets/
            ├── variables.css   # Design tokens
            ├── base.css        # Global reset + typography
            ├── layout.css      # Container, header, grid layout
            └── components.css  # Buttons, cards, modals, forms, toast, pagination
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- A browser with ES Module support (any modern browser)

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Flask Server

```bash
python run.py
```

The API is now available at `http://127.0.0.1:5000`.

### 3. Seed Sample Data *(optional)*

```bash
python seed.py
```

Inserts 5 sample recipes. Running it again is safe — it skips if recipes already exist.

### 4. Open the Frontend

Open `frontend/public/index.html` in your browser.  
> **Tip:** Use VS Code's **Live Server** extension for the best experience (auto-reloads on save and avoids CORS issues from `file://`).

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/recipes` | List recipes (paginated) |
| `POST` | `/api/recipes` | Create a recipe |
| `GET` | `/api/recipes/<id>` | Get a single recipe |
| `PUT` | `/api/recipes/<id>` | Update a recipe |
| `DELETE` | `/api/recipes/<id>` | Delete a recipe |
| `GET` | `/uploads/<filename>` | Serve an uploaded image |

### Pagination Query Params (`GET /api/recipes`)

| Param | Default | Max | Description |
|-------|---------|-----|-------------|
| `page` | `1` | — | Page number |
| `per_page` | `12` | `100` | Results per page |

**Response envelope:**
```json
{
  "recipes": [...],
  "total": 25,
  "page": 1,
  "per_page": 12,
  "pages": 3
}
```

### POST / PUT Form Fields

| Field | Type | Required |
|-------|------|----------|
| `title` | text | ✅ |
| `description` | text | ✅ |
| `ingredients` | text | ✅ |
| `instructions` | text | ✅ |
| `image` | file (png/jpg/jpeg/webp, max 5 MB) | ❌ |

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## Configuration

The frontend API URL is set in [`frontend/src/config.js`](frontend/src/config.js).  
Change `API_BASE` there and it propagates everywhere automatically.

```js
export const API_BASE = 'http://127.0.0.1:5000';
```

---

## Security Notes

- CORS is restricted to known local origins in `app/__init__.py`. Update `ALLOWED_ORIGINS` for staging/production.
- File uploads are secured with `werkzeug.utils.secure_filename` and UUID prefixes.
- All recipe data is HTML-escaped before rendering to prevent XSS.
- File type validation is performed server-side (extension whitelist).
