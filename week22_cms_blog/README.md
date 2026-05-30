# Week 22: Blog with CMS Backend

**Category:** Full Stack | **Status:** Completed

## About

This project is where everything converges. The CMS (Content Management System) is the most architecturally complete project in Phase 2 so far, combining a production-grade Flask backend with a decoupled, modular JavaScript frontend.

The backend is organized using the Application Factory pattern with Flask Blueprints, splitting concerns into `api/`, `models/`, and `extensions/` directories inside the `app/` package. The frontend is divided into three distinct surfaces: the public-facing blog (`public/`), the authenticated admin dashboard (`admin/`), and shared source modules (`src/`) for the API client, page logic, and utilities.

Content is written in Markdown and rendered in the browser using `marked.js`. All rendered output is sanitized with `DOMPurify` to prevent Cross-Site Scripting (XSS). Access to the admin panel is gated behind a JWT authentication flow.

## What It Does

A fully-featured CMS with a public-facing blog and a password-protected admin dashboard. Admins can create, edit, and manage posts, toggling their status between Draft and Published. Only Published posts appear on the public feed.

## Learning Objectives

- Application Factory pattern and Flask Blueprints for large-scale backend organization
- JWT authentication protecting API routes and admin UI
- Draft/Published content state workflows
- Markdown parsing with XSS sanitization using DOMPurify
- Modular CSS architecture split across `admin.css`, `modal.css`, and `toast.css`

## Project Structure

```
week22_cms_blog/
├── backend/
│   ├── run.py              # Application entry point
│   ├── config.py           # Configuration loader
│   ├── schema.sql          # Database schema
│   ├── seed.py             # Seed script for initial admin user
│   ├── data/               # SQLite database file
│   ├── tests/              # Pytest test suite
│   └── app/
│       ├── __init__.py     # Application factory
│       ├── api/            # Blueprint: API route handlers
│       ├── models/         # Database query functions
│       └── extensions/     # Flask extensions (JWT, CORS)
└── frontend/
    ├── public/             # Public-facing blog (index.html + public.css)
    ├── admin/              # Admin dashboard (index.html + css/)
    └── src/
        ├── api/            # Shared API client (client.js)
        ├── pages/          # Page-level JS (admin.js, public.js)
        └── utils/          # Auth utility (auth.js)
```

## Tech Stack

- **Backend:** Python, Flask, Flask-JWT-Extended, Flask-CORS, bcrypt
- **Database:** SQLite
- **Frontend:** HTML, CSS, Vanilla JavaScript (ES Modules), marked.js, DOMPurify
