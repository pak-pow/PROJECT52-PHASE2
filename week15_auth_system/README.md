# Week 15: User Authentication System

**Category:** Backend Security | **Status:** Completed

## About

An application is not truly personal until it knows who is using it. This project builds a complete authentication system from the ground up — registration, login, and protected routes — using cryptographic best practices.

The backend runs as a Flask API in `src/app.py` while the frontend (`src/index.html`, `src/script.js`) provides the login and registration UI. Data is persisted in an SQLite database (`users.db`). No plain-text passwords are ever stored; every password is hashed and salted with `bcrypt` before touching the database, and sessions are managed using stateless JSON Web Tokens (JWT).

## What It Does

A full authentication pipeline: users can register an account, log in to receive a JWT, and use that token to access protected endpoints.

## Learning Objectives

- Password cryptography using `bcrypt` (hashing and salting)
- Stateless session management via JSON Web Tokens (JWT)
- Building protected route middleware that validates tokens on every request
- Secure storage of credentials in an SQLite database

## Project Structure

```
week15_auth_system/
├── requirement.txt         # Python dependencies
├── users.db                # SQLite database (gitignored)
└── src/
    ├── app.py              # Flask API: registration, login, protected routes
    ├── index.html          # Login and registration UI
    ├── script.js           # Frontend auth logic
    └── style.css           # Styling
```

## Tech Stack

- **Backend:** Python, Flask, Flask-JWT-Extended, bcrypt
- **Database:** SQLite
- **Frontend:** HTML, CSS, Vanilla JavaScript
