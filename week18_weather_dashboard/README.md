# Week 18: Weather Dashboard with API

**Category:** Full Stack | **Status:** Completed

## About

The true power of the web lies in its interconnectedness. This project connects to a real third-party weather API to fetch and display live meteorological data. The focus is on learning how to read external API documentation, handle API keys securely, and manage the asynchronous complexity of depending on an external service you do not control.

The JavaScript is intentionally split into three separate module files to practice separation of concerns: `api.js` handles all HTTP communication, `ui.js` manages all DOM rendering, and `app.js` serves as the entry point that wires them together.

## What It Does

A weather dashboard that accepts a city name from the user and displays real-time weather conditions by fetching live data from an external weather API.

## Learning Objectives

- Authenticating and querying third-party external APIs
- Parsing complex, deeply nested JSON responses
- Managing loading states and handling network failures gracefully
- Separating concerns across JavaScript modules (`api.js`, `ui.js`, `app.js`)

## Project Structure

```
week18_weather_dashboard/
├── index.html      # Application markup
├── css/
│   └── style.css   # Styling
└── js/
    ├── api.js      # Handles all fetch calls to the weather API
    ├── ui.js       # All DOM manipulation and rendering
    └── app.js      # Entry point, wires api.js and ui.js together
```

## Tech Stack

- **Frontend:** HTML, CSS, Vanilla JavaScript (ES Modules)
- **Data:** External Weather API
