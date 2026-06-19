-- Idempotent schema: safe to run on an existing database
CREATE TABLE IF NOT EXISTS recipes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT NOT NULL,
    description      TEXT NOT NULL,
    ingredients      TEXT NOT NULL,
    instructions     TEXT NOT NULL,
    image_filename   TEXT,
    category         TEXT DEFAULT 'Uncategorised',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Migration: add category column to existing databases that pre-date Day 7
-- SQLite does not support IF NOT EXISTS on ALTER TABLE, so we ignore the error
-- if the column already exists. The Python migration script handles this gracefully.