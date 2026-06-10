-- =============================================================================
-- Week 24 — URL Shortener | Database Schema
-- =============================================================================

CREATE TABLE IF NOT EXISTS urls (
    id           INTEGER   PRIMARY KEY AUTOINCREMENT,
    original_url TEXT      NOT NULL,
    short_code   VARCHAR(10) UNIQUE NOT NULL,
    clicks       INTEGER   DEFAULT 0,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at   TIMESTAMP NULL
);

-- Index on short_code: every redirect hits this lookup, it must be O(log n)
CREATE INDEX IF NOT EXISTS idx_short_code ON urls (short_code);
