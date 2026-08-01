# 📅 Week 31 — Full-Stack Booking & Appointment System

A modern, high-performance Full-Stack Booking & Appointment System built with Python Flask, SQLite (WAL mode), modular ES6 JavaScript, and custom CSS design system with Dark/Light theme tokens.

---

## 🌟 Key Features

1. **Dynamic Availability Engine**: Computes open 30-minute time slots dynamically based on specialist working hours, day-of-week schedules, and existing confirmed bookings.
2. **Double-Booking Prevention**: Database-level and SQL query overlap checks prevent conflicting appointments even under concurrent requests.
3. **Interactive Calendar & Slot Picker**: Month-view calendar widget with date navigation and visual time slot pill buttons (`Available` vs `Booked`).
4. **Service Catalog Search & Sort**: Real-time keyword search and multi-attribute sorting (`Price: Low to High`, `Price: High to Low`, `Duration: Shortest`).
5. **Client Dashboard**: 3-tab categorized appointment dashboard (`Upcoming`, `Past`, `Cancelled`) with 1-click appointment cancellation.
6. **Specialist Agenda Timeline**: Provider schedule view (`provider.html`) displaying daily hour-by-hour appointment agendas for any specialist.
7. **Session & Security Isolation**: Bearer token authentication, pass-hash security (`Werkzeug`), and automatic session flushes on login screens.

---

## 🏗️ Architecture & Project Structure

```
week31_booking_system/
├── backend/
│   ├── app/
│   │   ├── config/
│   │   │   └── settings.py           # Flask & SQLite Config
│   │   ├── models/
│   │   │   ├── user_model.py         # Registration & Auth
│   │   │   ├── session_model.py      # Bearer Tokens
│   │   │   ├── service_model.py      # Service Catalog
│   │   │   ├── provider_model.py     # Specialist Queries & Availability
│   │   │   └── booking_model.py      # Overlap Query & Booking Creation
│   │   ├── routes/
│   │   │   ├── health_routes.py      # GET /api/health
│   │   │   ├── auth_routes.py        # /api/auth/*
│   │   │   ├── service_routes.py     # /api/services/*
│   │   │   ├── provider_routes.py    # /api/providers/*
│   │   │   └── booking_routes.py     # /api/bookings/*
│   │   ├── services/
│   │   │   ├── availability_service.py # Time Slot Calculation Engine
│   │   │   ├── serializers.py        # Model-to-JSON Serializers
│   │   │   └── auth_service.py       # @require_auth Decorator
│   │   ├── db.py                     # SQLite Connection Factory
│   │   └── __init__.py               # Flask App Factory & CORS
│   ├── data/
│   │   ├── schema.sql                # SQLite WAL Mode Schema
│   │   └── seed.py                   # Initial Database Seeder
│   ├── tests/
│   │   └── test_booking_routes.py    # Pytest Test Suite (7/7 Passed)
│   └── run.py                        # Server Entrypoint (Port 5000)
└── frontend/
    ├── public/
    │   ├── index.html                # Service Catalog Homepage
    │   ├── login.html                # Login Screen
    │   ├── register.html             # User Registration Screen
    │   ├── book.html                 # Booking Checkout Wizard
    │   ├── dashboard.html            # User Appointments Dashboard
    │   └── provider.html             # Specialist Schedule Agenda
    └── src/
        ├── api/                      # Fetch API Wrappers (auth, service, booking)
        ├── assets/                   # CSS Design Tokens & Stylesheets
        ├── components/               # Navbar, Calendar, SlotPicker Widgets
        ├── pages/                    # Page Controller Modules
        └── utils/                    # Theme, Auth, and Helper Utilities
```

---

## 🚀 Quick Start Guide

### 1. Start Backend Server
```bash
cd week31_booking_system/backend
python run.py
```
The server will run on `http://127.0.0.1:5000`.

### 2. Run Test Suite
```bash
cd week31_booking_system/backend
python -m pytest tests/ -v
```

### 3. Serve Frontend
Open `frontend/public/index.html` in your browser or run a simple local web server:
```bash
cd week31_booking_system/frontend/public
python -m http.server 8000
```

---

## 🔌 REST API Reference Table

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | No | System health check & metadata |
| `POST` | `/api/auth/register` | No | User account creation & token issuance |
| `POST` | `/api/auth/login` | No | Authenticate user & issue token |
| `GET` | `/api/auth/me` | Yes | Get currently authenticated user profile |
| `POST` | `/api/auth/logout` | Yes | Invalidate user session token |
| `GET` | `/api/services` | No | List service catalog (optional `?category=`) |
| `GET` | `/api/services/<id>` | No | Get service details & qualified providers |
| `GET` | `/api/providers` | No | List all specialists |
| `GET` | `/api/providers/<id>/availability` | No | Compute open time slots (`?service_id=&date=`) |
| `POST` | `/api/bookings` | Yes | Reserve appointment (checks double-booking) |
| `GET` | `/api/bookings/my-bookings` | Yes | Get client's booked appointments |
| `DELETE` | `/api/bookings/<id>` | Yes | Cancel an appointment |

---

## 🗄️ Database Schema & Models

- **`users`**: Client and Provider accounts (`username`, `email`, `password_hash`, `role`).
- **`sessions`**: Active Bearer authentication tokens (`token`, `expires_at`).
- **`services`**: Service catalog (`title`, `description`, `duration_minutes`, `price`, `category`).
- **`providers`**: Specialist details (`user_id`, `title`, `bio`).
- **`provider_services`**: Junction table mapping specialists to services they are qualified to perform.
- **`provider_availability`**: Weekly working schedules (`provider_id`, `day_of_week`, `start_time`, `end_time`).
- **`bookings`**: Appointment reservations (`user_id`, `provider_id`, `service_id`, `booking_date`, `start_time`, `end_time`, `status`, `notes`).
