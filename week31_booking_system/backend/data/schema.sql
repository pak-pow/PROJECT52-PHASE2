-- ══════════════════════════════════════════════════════════════
--  Week 31 — Booking & Appointment System  |  SQLite Schema
-- ══════════════════════════════════════════════════════════════
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ── Users ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER  PRIMARY KEY AUTOINCREMENT,
    username      TEXT     NOT NULL UNIQUE COLLATE NOCASE
                           CHECK(length(username) >= 3 AND length(username) <= 30),
    display_name  TEXT     NOT NULL,
    email         TEXT     NOT NULL UNIQUE COLLATE NOCASE,
    role          TEXT     NOT NULL DEFAULT 'client'
                           CHECK(role IN ('client', 'provider', 'admin')),
    password_hash TEXT     NOT NULL,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── Sessions (Bearer Token Auth) ──────────────────────────────
CREATE TABLE IF NOT EXISTS sessions (
    token      TEXT     PRIMARY KEY,
    user_id    INTEGER  NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── Services (Catalog of Offered Services) ─────────────────────
CREATE TABLE IF NOT EXISTS services (
    id               INTEGER  PRIMARY KEY AUTOINCREMENT,
    title            TEXT     NOT NULL,
    description      TEXT     NOT NULL DEFAULT '',
    duration_minutes INTEGER  NOT NULL DEFAULT 30 CHECK(duration_minutes > 0),
    price            REAL     NOT NULL DEFAULT 0.0 CHECK(price >= 0),
    category         TEXT     NOT NULL DEFAULT 'General',
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── Providers (Staff / Service Providers) ─────────────────────
CREATE TABLE IF NOT EXISTS providers (
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER  NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    title      TEXT     NOT NULL DEFAULT 'Specialist',
    bio        TEXT     NOT NULL DEFAULT '',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── Provider Services (M:N Mapping) ───────────────────────────
CREATE TABLE IF NOT EXISTS provider_services (
    provider_id INTEGER NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    service_id  INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    PRIMARY KEY (provider_id, service_id)
);

-- ── Provider Weekly Schedules (Working Hours) ────────────────
CREATE TABLE IF NOT EXISTS provider_availability (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_id INTEGER NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK(day_of_week BETWEEN 0 AND 6), -- 0=Mon, 6=Sun
    start_time  TEXT    NOT NULL, -- e.g. "09:00"
    end_time    TEXT    NOT NULL  -- e.g. "17:00"
);

-- ── Bookings (Appointments) ───────────────────────────────────
CREATE TABLE IF NOT EXISTS bookings (
    id           INTEGER  PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER  NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider_id  INTEGER  NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    service_id   INTEGER  NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    booking_date TEXT     NOT NULL, -- YYYY-MM-DD
    start_time   TEXT     NOT NULL, -- HH:MM
    end_time     TEXT     NOT NULL, -- HH:MM
    status       TEXT     NOT NULL DEFAULT 'confirmed'
                          CHECK(status IN ('confirmed', 'cancelled', 'completed')),
    notes        TEXT     NOT NULL DEFAULT '',
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for lightning fast availability searches
CREATE INDEX IF NOT EXISTS idx_bookings_provider_date ON bookings(provider_id, booking_date, status);
CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id, status);
