-- =============================================================================
-- Week 24 — URL Shortener | Database Schema
-- =============================================================================

CREATE TABLE IF NOT EXISTS urls (
    id           INTEGER   PRIMARY KEY AUTOINCREMENT,
    original_url TEXT      NOT NULL,
    -- FIX: VARCHAR(20) to match the 20-char limit enforced in is_valid_alias()
    -- FIX: short_code is now nullable to avoid the "PENDING" placeholder DoS bug.
    --      A NULL short_code means a Base62 code is being generated for this row.
    short_code   VARCHAR(20) UNIQUE,
    clicks       INTEGER   DEFAULT 0,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at   TIMESTAMP NULL
);

-- Index on short_code: every redirect hits this lookup, it must be O(log n)
CREATE INDEX IF NOT EXISTS idx_short_code ON urls (short_code);
