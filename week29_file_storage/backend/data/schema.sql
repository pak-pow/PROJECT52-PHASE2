-- ═══════════════════════════════════════════════════════════════
--  Week 29 — File Upload & Storage System
--  Database Schema (SQLite)
-- ═══════════════════════════════════════════════════════════════

-- ── Users ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT    NOT NULL UNIQUE,
    password_hash   TEXT    NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── Sessions ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    token           TEXT    NOT NULL UNIQUE,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── Files ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS files (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    original_name   TEXT    NOT NULL,
    stored_name     TEXT    NOT NULL UNIQUE,
    mime_type       TEXT    NOT NULL,
    file_size       INTEGER NOT NULL,
    category        TEXT    DEFAULT 'other',
    has_thumbnail   BOOLEAN DEFAULT 0,
    uploaded_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
