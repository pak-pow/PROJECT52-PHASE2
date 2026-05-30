# Week 23: Expense Tracker with Charts

**Category:** Full Stack | **Status:** In Progress

## About

Transitioning from a CMS to an Expense Tracker introduces two concepts that are everywhere in enterprise software but rarely taught together: **data aggregation** and **data visualization**.

This project is not just a list of numbers. Raw expense records are grouped and summed by category using SQL aggregate functions (`GROUP BY`, `SUM()`), turned into structured data by the API, and then rendered as interactive charts on the frontend using Chart.js. The result is a financial analytics dashboard that turns a pile of transactions into a clear, visual breakdown of spending.

The backend uses the most advanced scaffold in the project so far — the Application Factory pattern with a full separation of concerns across `config/`, `models/`, `routes/`, `services/`, `middlewares/`, and `utils/` directories. The frontend mirrors this modularity with a `src/` directory containing `api/`, `pages/`, `components/`, and `utils/` folders.

## What It Does

A personal finance tracker where users log expenses with categories, amounts, and dates. The dashboard aggregates spending by category and renders the data as dynamic charts that update in real time as new entries are added.

## Learning Objectives

- SQL data aggregation: `GROUP BY`, `SUM()`, `ORDER BY`, and date-range filtering
- Using `DECIMAL(10,2)` for financial precision (avoiding float rounding errors)
- Integrating Chart.js to render pie charts and bar graphs from API data
- Designing a modular Flask backend with the Application Factory pattern

## Project Structure

```
week23_expense_tracker/
├── backend/
│   ├── run.py              # Application entry point
│   ├── schema.sql          # Database schema (users + expenses tables)
│   ├── seed.py             # Seed script
│   ├── data/               # SQLite database file
│   ├── tests/              # Pytest test suite
│   └── app/
│       ├── __init__.py     # Application factory
│       ├── config/         # Configuration loader
│       ├── models/         # Database query functions (expense.py)
│       ├── routes/         # API route handlers (expenses.py)
│       ├── services/       # Business logic layer
│       ├── middlewares/    # Auth and request middleware
│       └── utils/          # Shared helpers
└── frontend/
    ├── public/             # Static HTML entry point
    └── src/
        ├── main.js         # Frontend entry point
        ├── api/            # API client (client.js)
        ├── pages/          # Page-level logic
        ├── components/     # Reusable UI components
        └── utils/          # Shared frontend utilities
```

## Tech Stack

- **Backend:** Python, Flask, Flask-JWT-Extended, Flask-CORS, bcrypt
- **Database:** SQLite
- **Frontend:** HTML, CSS, Vanilla JavaScript (ES Modules), Chart.js
