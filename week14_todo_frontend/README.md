# Week 14: Todo Frontend with Fetch API

**Category:** Frontend + Backend Integration | **Status:** Completed

## About

After building a headless data engine in Week 13, this project gives it a face. The challenge here is not HTML or CSS — it is JavaScript. The entire UI must communicate with the backend API asynchronously, meaning the page never reloads. Every action the user takes (adding, completing, or deleting a task) is handled in the background via `fetch()` calls, and the DOM is updated programmatically in response.

This is the foundation of how every modern single-page application works.

## What It Does

A dynamic, JavaScript-driven Todo interface that consumes the Week 13 REST API. All data fetching, creation, and deletion happen without a page refresh.

## Learning Objectives

- Asynchronous JavaScript using `async/await` and Promises
- Making HTTP requests from the browser using the `Fetch API`
- Dynamically creating, updating, and removing DOM elements based on API responses
- Handling network errors and API failures gracefully in the UI

## Project Structure

```
week14_todo_frontend/
├── index.html      # Application shell and markup
├── app.js          # All API calls and DOM manipulation logic
└── style.css       # Styling
```

## Tech Stack

- **Frontend:** HTML, CSS, Vanilla JavaScript
- **API:** Fetch API (consuming the Week 13 Flask backend)
