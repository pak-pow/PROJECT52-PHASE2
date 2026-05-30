# Week 20: E-commerce Product Catalog

**Category:** Full Stack | **Status:** Completed

## About

E-commerce is one of the most demanding domains in web development. This project builds the core engine of a digital storefront: the product catalog. The backend manages a database of products with categories, prices, and descriptions, while the frontend tackles the genuinely hard problem of multi-layered filtering and search — letting users slice through inventory in real time without hammering the server on every keystroke.

The backend follows a clean two-file structure: `app.py` exposes the API endpoints, while `init_db.py` handles database initialization and seeding. The frontend is a single-page experience with all product rendering handled in `app.js`.

## What It Does

A browsable product catalog with category filtering and a search bar, backed by a Flask API connected to an SQLite product database.

## Learning Objectives

- Designing a database schema for products with categories and attributes
- Writing backend filter logic that handles multiple overlapping query parameters
- Frontend state management: tracking active filters and search terms simultaneously
- Debouncing input events to avoid spamming the API

## Project Structure

```
week20_ecommerce_catalog/
├── backend/
│   ├── app.py          # Flask API with filtering and search endpoints
│   ├── init_db.py      # Database initialization and seed data script
│   └── data/           # SQLite database file
└── frontend/
    ├── index.html      # Product grid UI
    ├── app.js          # Filter, search, and rendering logic
    └── style.css       # Styling
```

## Tech Stack

- **Backend:** Python, Flask, SQLite
- **Frontend:** HTML, CSS, Vanilla JavaScript
