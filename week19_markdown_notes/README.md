# Week 19 — Markdown Note-Taking App

**Goal:** A full-stack application that reads, writes, and parses local Markdown files.

**MVP Acceptance Criteria**
- [ ] Backend API can list, read, save, and delete `.md` files.
- [ ] Frontend displays a list of notes.
- [ ] Frontend features a split-pane: raw text editor on the left, live HTML preview on the right.
- [ ] Notes are persisted locally in the `backend/data/` directory.

**How to run**
1. `cd backend && pip install -r ../requirements.txt`
2. `python app.py` (Runs API on port 5000)
3. Open `frontend/index.html` via Live Server.