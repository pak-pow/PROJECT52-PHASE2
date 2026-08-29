-- SQLite Schema for Week 35 Notification System

-- Templates Table (Email, SMS, Webhook Templates)
CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    channel VARCHAR(30) NOT NULL, -- 'email', 'sms', 'webhook'
    subject VARCHAR(200),        -- Optional subject line for emails
    body_template TEXT NOT NULL,  -- Jinja2 template with {{ variables }}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Preferences Table (Opt-in / Opt-out Channels)
CREATE TABLE IF NOT EXISTS user_preferences (
    user_id INTEGER PRIMARY KEY,
    email_enabled INTEGER DEFAULT 1,
    sms_enabled INTEGER DEFAULT 1,
    webhook_enabled INTEGER DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications Audit Log & Queue Table
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idempotency_key VARCHAR(120) UNIQUE,
    user_id INTEGER NOT NULL,
    recipient VARCHAR(200) NOT NULL, -- Email address, phone number, or webhook URL
    channel VARCHAR(30) NOT NULL,    -- 'email', 'sms', 'webhook'
    template_name VARCHAR(100),
    subject VARCHAR(200),
    content TEXT NOT NULL,
    variables_json TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'Queued', -- 'Queued', 'Processing', 'Sent', 'Failed', 'Skipped'
    attempts INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    FOREIGN KEY (template_name) REFERENCES templates(name) ON DELETE SET NULL
);

-- Indexes for Fast Status & User Queries
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_idempotency ON notifications(idempotency_key);
