# Week 21: Real-time Chat Application

**Category:** Full Stack | **Status:** Completed

## About

Every project up to this point has operated on the traditional HTTP request-response cycle: the client asks, the server answers, and the connection closes. This project breaks that pattern entirely.

Using WebSockets via Socket.IO, the server and client maintain a persistent, open connection. When one user sends a message, the server pushes it to all connected clients instantly — no polling, no page refresh. This is the same technology that powers Slack, Discord, and live trading platforms. It is a completely different programming model: event-driven rather than request-driven.

## What It Does

A real-time chat application where multiple users can connect and exchange messages instantly. Messages are persisted in a SQLite database so chat history survives reconnections.

## Learning Objectives

- WebSocket protocol and how it differs fundamentally from HTTP
- Event-driven architecture: emitting and listening for named events
- Managing multiple simultaneous client connections on the server
- Synchronizing state across all connected clients in real time

## Project Structure

```
week21_chat_app/
├── backend/
│   └── app.py          # Flask-SocketIO server with event handlers
└── frontend/
    ├── index.html      # Chat UI
    ├── app.js          # Socket.IO client logic
    └── style.css       # Styling
```

## Tech Stack

- **Backend:** Python, Flask, Flask-SocketIO
- **Frontend:** HTML, CSS, Vanilla JavaScript, Socket.IO client
- **Database:** SQLite (message persistence)
