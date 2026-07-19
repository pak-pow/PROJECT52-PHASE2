-- ══════════════════════════════════════════════════════════════
--  Week 30 — Social Media Feed  |  SQLite Schema
-- ══════════════════════════════════════════════════════════════
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ── Users ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER  PRIMARY KEY AUTOINCREMENT,
    username      TEXT     NOT NULL UNIQUE COLLATE NOCASE
                           CHECK(length(username) >= 3 AND length(username) <= 30),
    display_name  TEXT     NOT NULL,
    bio           TEXT     NOT NULL DEFAULT ''
                           CHECK(length(bio) <= 160),
    avatar_path   TEXT,
    password_hash TEXT     NOT NULL,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── Sessions (Bearer token auth) ──────────────────────────────
CREATE TABLE IF NOT EXISTS sessions (
    token      TEXT     PRIMARY KEY,
    user_id    INTEGER  NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── Posts ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS posts (
    id            INTEGER  PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER  NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content       TEXT     NOT NULL DEFAULT ''
                           CHECK(length(content) <= 280),
    image_path    TEXT,
    reply_to_id   INTEGER  REFERENCES posts(id) ON DELETE SET NULL,
    repost_of_id  INTEGER  REFERENCES posts(id) ON DELETE SET NULL,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- must have content OR image
    CHECK(length(content) > 0 OR image_path IS NOT NULL)
);

-- ── Likes (compound PK prevents duplicate likes) ───────────────
CREATE TABLE IF NOT EXISTS likes (
    user_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id  INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, post_id)
);

-- ── Follows ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS follows (
    follower_id  INTEGER  NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id INTEGER  NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, following_id),
    CHECK(follower_id != following_id)
);

-- ── Indexes ────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_posts_user_id     ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_reply_to    ON posts(reply_to_id);
CREATE INDEX IF NOT EXISTS idx_posts_repost_of   ON posts(repost_of_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at  ON posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_likes_post_id     ON likes(post_id);
CREATE INDEX IF NOT EXISTS idx_follows_follower  ON follows(follower_id);
CREATE INDEX IF NOT EXISTS idx_follows_following ON follows(following_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id  ON sessions(user_id);
