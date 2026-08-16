-- SQLite Schema for Week 34 Job Board Platform

DROP TABLE IF EXISTS saved_jobs;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS users;

-- Users Table (Employers and Job Seekers)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'applicant', -- 'employer' or 'applicant'
    company_name VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jobs Table
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_id INTEGER NOT NULL,
    title VARCHAR(150) NOT NULL,
    company VARCHAR(120) NOT NULL,
    location VARCHAR(120) NOT NULL,
    job_type VARCHAR(50) NOT NULL DEFAULT 'Full-time', -- 'Full-time', 'Part-time', 'Contract', 'Remote'
    salary_min INTEGER DEFAULT 0,
    salary_max INTEGER DEFAULT 0,
    category VARCHAR(80) NOT NULL DEFAULT 'Engineering',
    description TEXT NOT NULL,
    requirements TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employer_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Job Applications Table
CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    applicant_id INTEGER,
    applicant_name VARCHAR(120) NOT NULL,
    applicant_email VARCHAR(120) NOT NULL,
    resume_path VARCHAR(255),
    cover_letter TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'Pending', -- 'Pending', 'Reviewing', 'Interviewing', 'Accepted', 'Rejected'
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (applicant_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Saved Jobs Bookmarks Table
CREATE TABLE saved_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Indexes for Fast Querying & Filtering
CREATE INDEX idx_jobs_category ON jobs(category);
CREATE INDEX idx_jobs_job_type ON jobs(job_type);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_applications_job_id ON applications(job_id);
CREATE INDEX idx_applications_applicant_id ON applications(applicant_id);
