# Week 17: SQLite Database Manager

**Category:** Backend + Database | **Status:** Completed

## About

This project strips away the abstractions and gets directly hands-on with raw SQL. Instead of using an ORM (Object-Relational Mapper) that hides the database behind Python objects, every query in this project is written by hand. This builds a deep understanding of how data is stored, related, updated, and retrieved — knowledge that underpins every major framework.

The project is split into two parts: a Python command-line interface (`main.py` and `db_manager.py`) for direct database interaction, and a lightweight web interface (`web/`) for performing those same CRUD operations through a browser.

## What It Does

A SQLite database management tool with both a Python CLI and a browser-based web interface for running CRUD operations directly against a local database.

## Learning Objectives

- Relational database design: tables, primary keys, and foreign key constraints
- Writing raw SQL: `SELECT`, `INSERT`, `UPDATE`, `DELETE`
- Understanding data integrity, `UNIQUE` constraints, and cascading operations
- Safely connecting a Python application to a SQLite database file

## Project Structure

```
week17_sqlite_manager/
├── app.py              # Flask web server
├── db_manager.py       # Python database connection and query helpers
├── main.py             # CLI entry point for database operations
├── project52.db        # Primary SQLite database file
└── web/
    ├── index.html      # Browser-based database UI
    ├── script.js       # Frontend logic
    └── style.css       # Styling
```

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite (raw SQL, no ORM)
- **Frontend:** HTML, CSS, Vanilla JavaScript
