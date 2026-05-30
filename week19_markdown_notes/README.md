# Week 19: Markdown Note-Taking App

**Category:** Full Stack | **Status:** Completed

## About

Developers live in Markdown. This project builds a full-stack note-taking application where notes are written in Markdown, saved as actual `.md` files on the server's filesystem via a Python Flask backend, and rendered as rich HTML in the browser.

This introduces a class of problems not covered by simple CRUD APIs: file system I/O, persisting data as real files rather than database rows, and the security implications of rendering user-written HTML (XSS).

## What It Does

A note-taking app where users write notes in Markdown syntax. The backend stores them as files on disk and serves them back; the frontend renders them as styled HTML.

## Learning Objectives

- File system I/O in Python: reading, writing, and deleting files safely
- Parsing and converting Markdown to HTML on the frontend
- Keeping a frontend UI synchronized with the physical state of the server's file system
- Understanding XSS risks when rendering user-generated HTML content

## Project Structure

```
week19_markdown_notes/
├── requirements.txt
├── backend/
│   ├── app.py          # Flask API for reading/writing .md files
│   └── data/           # Directory where .md note files are stored
└── frontend/
    ├── index.html      # Note editor and preview UI
    ├── app.js          # Frontend logic: fetch notes, render Markdown
    └── style.css       # Styling
```

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, Vanilla JavaScript, marked.js (Markdown parser)
- **Storage:** Server-side `.md` files
