-- ============================================================
--  Week 27: Portfolio v2 — Database Schema
-- ============================================================

-- Contact form submissions from visitors
CREATE TABLE IF NOT EXISTS contact_messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL,
    subject     TEXT NOT NULL,
    message     TEXT NOT NULL,
    is_read     INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Portfolio projects (DB-driven, CRUD via admin panel)
CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    description TEXT NOT NULL,
    tech_stack  TEXT NOT NULL,
    github_url  TEXT,
    live_url    TEXT,
    status      TEXT DEFAULT 'In Progress',
    sort_order  INTEGER DEFAULT 0,
    featured    INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin sessions (simple token-based auth, no JWT library)
CREATE TABLE IF NOT EXISTS admin_sessions (
    token       TEXT PRIMARY KEY,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at  TIMESTAMP NOT NULL
);

-- ============================================================
--  Seed Data: Pre-populate projects from v1
-- ============================================================
INSERT OR IGNORE INTO projects (id, title, description, tech_stack, github_url, status, sort_order, featured)
VALUES
    (1, 'PROJECT_PYGAME',
        'A 3D Engine built from scratch in Python using Pygame and OpenGL. Custom renderer, matrix transforms, and camera system.',
        'Python, Pygame, OpenGL',
        'https://github.com/pak-pow/PROJECT_PYGAME',
        'Completed', 1, 1),
    (2, 'PROJECT52: Phase 1',
        '12-week sprint building foundational projects: portfolio, CLI tools, data visualisation, web scraper, quiz app, and more.',
        'Python, HTML, CSS, JavaScript',
        'https://github.com/pak-pow/PROJECT52-PHASE1',
        'Completed', 2, 0),
    (3, 'PROJECT52: Phase 2',
        '24-week full-stack integration phase: REST APIs, authentication, real-time chat, Kanban board, and this portfolio.',
        'Python, Flask, SQLite, JavaScript',
        'https://github.com/pak-pow/PROJECT52-PHASE2',
        'In Progress', 3, 0),
    (4, 'PROJECT52: Phase 3',
        'Production-ready applications: deployment, DevOps, testing, scalability, and cloud infrastructure.',
        'Docker, CI/CD, PostgreSQL, Cloud',
        'https://github.com/pak-pow/PROJECT52-PHASE3',
        'Planned', 4, 0);
