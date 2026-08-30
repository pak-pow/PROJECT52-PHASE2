-- SQLite Schema for Week 36 Analytics Dashboard

DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS funnel_steps;
DROP TABLE IF EXISTS funnels;

-- Events Telemetry Table
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name VARCHAR(100) NOT NULL, -- 'pageview', 'click', 'signup', 'purchase', etc.
    session_id VARCHAR(120) NOT NULL,
    user_id VARCHAR(100),             -- Optional authenticated user ID
    url_path VARCHAR(500) NOT NULL,   -- e.g. '/dashboard', '/products/42'
    referrer VARCHAR(500),            -- e.g. 'https://google.com', 'https://twitter.com'
    device_type VARCHAR(30) NOT NULL DEFAULT 'desktop', -- 'desktop', 'mobile', 'tablet'
    browser VARCHAR(50) NOT NULL DEFAULT 'Chrome',      -- 'Chrome', 'Safari', 'Firefox', 'Edge'
    os VARCHAR(50) NOT NULL DEFAULT 'Windows',          -- 'Windows', 'MacOS', 'iOS', 'Android', 'Linux'
    country VARCHAR(50) NOT NULL DEFAULT 'United States',
    metadata_json TEXT,               -- Additional custom JSON payload
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Funnels Definition Table
CREATE TABLE funnels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Funnel Steps Table
CREATE TABLE funnel_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funnel_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    event_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (funnel_id) REFERENCES funnels(id) ON DELETE CASCADE
);

-- Indexes for Fast Time-Series and Analytical Queries
CREATE INDEX idx_events_created_at ON events(created_at);
CREATE INDEX idx_events_event_name ON events(event_name);
CREATE INDEX idx_events_session_id ON events(session_id);
CREATE INDEX idx_events_url_path ON events(url_path);
CREATE INDEX idx_events_device_type ON events(device_type);
CREATE INDEX idx_events_country ON events(country);
CREATE INDEX idx_funnel_steps_funnel_id ON funnel_steps(funnel_id, step_order);
