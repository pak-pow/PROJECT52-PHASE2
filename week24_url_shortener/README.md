# Week 24: URL Shortener Service

**Category:** Backend | **Status:** Completed

## About

A full-stack URL shortening service that takes long destination URLs and generates short, unique aliases. When a user requests a short URL, the server performs a 302 redirect to the original destination. To make the project production-ready, it features URL collision resolution, custom alias naming, and redirection traffic analytics.

## What It Does

- Shortens long URLs into unique 6-character hashes
- Detects and resolves collision conflicts dynamically
- Allows custom user-defined aliases (e.g. `/my-link`)
- Tracks usage stats (click count, last accessed date)
- Renders an interactive landing page to shorten and manage links

## Learning Objectives

- Designing compact hash generators (base62 encoding / MD5 truncating)
- Handling dynamic HTTP redirections (`302 Found`)
- Managing relational database mappings for URLs and analytics
- Implementing custom validation rules (URI formatting, alias blacklists)

## Project Structure

```
week24_url_shortener/
├── backend/
│   ├── app.py              # Flask app factory
│   ├── config.py           # Configuration (Flask, SQLite paths)
│   ├── requirements.txt
│   ├── run.py              # Backend entrypoint
│   ├── app/
│   │   ├── config/
│   │   ├── routes/         # Shortener and redirect endpoints
│   │   ├── services/       # Base62 hash generation logic
│   │   ├── models/         # Database models
│   │   ├── middlewares/
│   │   └── utils/
│   ├── data/
│   │   └── schema.sql      # Database schema
│   └── tests/
│       └── test_shortener.py
└── frontend/
    ├── package.json
    ├── public/
    │   └── index.html      # Landing page UI
    └── src/
        ├── main.js
        ├── assets/
        │   └── style.css
        └── api/
```

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** Vanilla JS, HTML, CSS
- **Database:** SQLite
