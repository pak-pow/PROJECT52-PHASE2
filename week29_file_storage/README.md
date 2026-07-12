# Week 29 — File Upload & Storage System

A full-stack file management platform where authenticated users can upload, organize, preview, and download files. Built with **Flask** (backend) and **vanilla JavaScript** (frontend).

## Features

- **User Authentication** — Register/login with token-based session auth
- **Drag-and-Drop Uploads** — Premium dropzone with progress bars
- **File Gallery** — Grid view with thumbnails, category badges, and animated cards
- **Preview Modal** — Full-size image preview with metadata details
- **Category Filters** — Filter by Images, Documents, Audio, Video, or Other
- **Auto-Thumbnails** — 200×200 JPEG thumbnails generated for uploaded images (Pillow)
- **File Validation** — MIME type whitelist, 10 MB size limit
- **Safe Storage** — UUID-based filenames prevent path traversal and collisions
- **Storage Abstraction** — Local filesystem adapter with a cloud-ready interface

## Tech Stack

| Layer     | Tech                                   |
|-----------|----------------------------------------|
| Backend   | Python, Flask, SQLite, Pillow          |
| Frontend  | HTML5, CSS3, Vanilla JavaScript (ES Modules) |
| Auth      | Token-based sessions (Bearer tokens)   |
| Server    | Waitress (production WSGI)             |
| Testing   | pytest                                 |

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python run.py
```
Backend runs at `http://localhost:5000`

### Frontend
Serve `frontend/public/` with any static server (e.g., VS Code Live Server on port 5500).

### Production
```bash
cd backend
python wsgi.py
```

## API Endpoints

| Method   | Endpoint                     | Auth | Description                    |
|----------|------------------------------|------|--------------------------------|
| `POST`   | `/api/auth/register`         | No   | Create a new user account      |
| `POST`   | `/api/auth/login`            | No   | Log in and receive a token     |
| `POST`   | `/api/auth/logout`           | Yes  | Invalidate session token       |
| `POST`   | `/api/files/upload`          | Yes  | Upload files (multipart)       |
| `GET`    | `/api/files`                 | Yes  | List files (optional `?category=`) |
| `GET`    | `/api/files/<id>`            | Yes  | Get single file metadata       |
| `GET`    | `/api/files/<id>/download`   | Yes  | Download the actual file       |
| `GET`    | `/api/files/<id>/thumbnail`  | Yes  | Serve the image thumbnail      |
| `DELETE` | `/api/files/<id>`            | Yes  | Delete file from disk and DB   |
| `GET`    | `/api/health`                | No   | Health check                   |

## Running Tests
```bash
cd backend
pytest -v
```

## Project Structure
```
week29_file_storage/
├── backend/
│   ├── app/
│   │   ├── config/settings.py      # File limits, MIME whitelist, paths
│   │   ├── db.py                   # SQLite connection helpers
│   │   ├── models/                 # file_model.py, user_model.py
│   │   ├── routes/                 # file_routes.py, auth_routes.py
│   │   ├── services/               # file_service.py, thumbnail_service.py, auth_service.py
│   │   └── storage/                # base.py (abstract), local.py (filesystem)
│   ├── data/schema.sql
│   ├── tests/
│   ├── run.py / wsgi.py
│   └── requirements.txt
└── frontend/
    ├── public/index.html
    └── src/
        ├── api/fileApi.js
        ├── assets/*.css
        ├── components/             # dropzone.js, preview.js
        ├── pages/                  # dashboard.js, upload.js
        ├── utils/helpers.js
        └── main.js
```
