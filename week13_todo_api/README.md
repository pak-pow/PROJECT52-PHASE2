# Week 13: REST API for Todo App

**Category:** Backend | **Status:** Completed

## About

This project marks the transition from writing standalone scripts to building a proper server. Instead of a monolithic application where logic and display are tangled together, this project is a decoupled data engine — a headless API that speaks purely in JSON and listens for HTTP requests.

The entire application lives in a single `app.py` file, which is intentional. The focus here is on understanding RESTful principles and HTTP semantics, not on project structure. Data is persisted to a `todos.json` file, keeping the setup lightweight and dependency-free.

## What It Does

A REST API that allows any client (browser, mobile app, Postman) to create, read, update, and delete todo items via standard HTTP requests.

## Learning Objectives

- RESTful API design and resource-based URL conventions
- HTTP methods: `GET`, `POST`, `PUT`, `DELETE` and when to use each
- Parsing incoming JSON request bodies and returning properly formatted JSON responses
- HTTP status codes and what they communicate to the client

## Project Structure

```
week13_todo_api/
├── app.py          # Flask application with all CRUD routes
└── todos.json      # JSON file used for data persistence
```

## Tech Stack

- **Backend:** Python, Flask
- **Storage:** JSON file (no database)
