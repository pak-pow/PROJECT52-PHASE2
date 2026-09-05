# 📊 Week 36 — Real-Time Analytics & Business Intelligence Dashboard

A production-grade, high-throughput **Real-Time Analytics & Business Intelligence Platform** built with Flask (Python), SQLite (WAL mode), Chart.js, and an interactive ES6 JavaScript frontend. Ingests high-volume visitor event telemetry (`pageview`, `click`, `signup`, `purchase`), parses HTTP `User-Agent` strings into browser/device/OS categories, computes time-series traffic metrics with growth deltas, evaluates multi-stage conversion funnels, streams live visitor activity in real-time, and exports downloadable CSV/JSON reports.

---

## 🏗️ System Architecture

```mermaid
graph TD
    Client["Client / Tracking Script / Web UI"] -->|1. POST /api/events (Telemetry)| EventRoute["Event Ingestion Controller (/api/events)"]
    Client -->|2. GET /api/analytics/overview| AnalyticsRoute["Analytics Metrics Controller (/api/analytics)"]
    Client -->|3. GET /api/funnels/<id>| FunnelRoute["Funnel Analysis Controller (/api/funnels)"]
    Client -->|4. GET /api/export/csv| ExportRoute["Export Controller (/api/export)"]
    
    EventRoute -->|Parse UA & Device| ParserService["UserAgent & Device Parser Service"]
    EventRoute -->|Insert Event Record| EventModel["EventModel (SQLite WAL)"]
    
    AnalyticsRoute -->|Time-Series Bucketing & Grouping| AggregationEngine["Time-Series Aggregation Engine"]
    AggregationEngine --> DB[("Analytics SQLite Database")]
    
    FunnelRoute -->|Step-by-Step Conversion Math| FunnelEngine["Funnel Calculation Engine"]
    FunnelEngine --> DB
```

---

## ✨ Key Features

- **High-Throughput Telemetry Ingestion**:
  - Single event tracking (`POST /api/events`) and batch event ingestion (`POST /api/events/batch`).
  - Automatic `User-Agent` parsing for **Browser** (`Chrome`, `Safari`, `Firefox`, `Edge`, `Opera`), **OS** (`Windows`, `MacOS`, `iOS`, `Android`, `Linux`), and **Device Type** (`desktop`, `mobile`, `tablet`).
  - Automatic referrer source categorization (`Search Engines`, `Social Media`, `Developer / Tech`, `Direct`).
- **Time-Series Aggregation Engine**:
  - Computes Total Pageviews, Unique Visitors (distinct `session_id`), Average Views per Session, and Bounce Rate (single-event sessions).
  - Previous period percentage comparison deltas (+14.2% vs previous period).
  - Flexible time-window bucketing by `hour`, `day`, or `month`.
  - Top performing content URLs ranked by view count and unique visitor reach.
- **Conversion Funnel Analytics Engine**:
  - Multi-stage sequential conversion tracking (Step 1 → Step 2 → Step 3 → Step 4).
  - Calculates step-by-step conversion percentages, drop-off counts, and overall funnel conversion rates.
- **Interactive Visualizations (Chart.js & CSS Grid)**:
  - **Traffic Area Chart**: Daily Pageviews vs Unique Visitors with responsive gradients and hover tooltips.
  - **Device & Browser Donut Charts**: Visual slice distributions.
  - **Top Pages & Sources Tables**: Searchable ranked content with percentage share progress bars.
  - **Funnel Visualizer**: Visual horizontal conversion bars with drop-off indicators.
- **Live Real-Time Activity Feed**:
  - Auto-polling real-time visitor event feed with event badges and an active live event counter.
  - Interactive **"Simulate Live Event"** button for real-time testing.
- **Data Export Engine**:
  - Instant CSV spreadsheet downloads (`GET /api/export/csv`) with attachment headers.
  - Structured JSON data export (`GET /api/export/json`).

---

## 🔌 REST API Reference Table

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Service health and total telemetry event count | `200 OK` |
| `POST` | `/api/events` | Ingest single visitor event with automatic UA parsing | `201 Created` / `400 Bad Request` |
| `POST` | `/api/events/batch` | Ingest multiple telemetry events in a single request | `201 Created` / `400 Bad Request` |
| `GET` | `/api/events/live` | Stream recent live visitor events (`?limit=50`) | `200 OK` |
| `GET` | `/api/analytics/overview` | KPI summary cards with period growth deltas | `200 OK` |
| `GET` | `/api/analytics/timeseries` | Traffic graphs grouped by `interval=hour\|day\|month` | `200 OK` |
| `GET` | `/api/analytics/breakdown` | Device, Browser, OS, Country, and Referrer distributions | `200 OK` |
| `GET` | `/api/analytics/top-pages` | Ranked top content URLs with percentage share | `200 OK` |
| `GET` | `/api/funnels` | List all registered conversion funnels | `200 OK` |
| `GET` | `/api/funnels/<id>` | Get funnel definition and steps | `200 OK` / `404 Not Found` |
| `GET` | `/api/funnels/<id>/metrics` | Calculate real-time conversion rates & drop-offs | `200 OK` / `404 Not Found` |
| `POST` | `/api/funnels` | Create new multi-stage conversion funnel | `201 Created` / `400 Bad Request` / `409 Conflict` |
| `GET` | `/api/export/csv` | Download streamable CSV spreadsheet (`?type=traffic\|events`) | `200 OK` |
| `GET` | `/api/export/json` | Structured JSON data export | `200 OK` |

---

## ⚡ Quick Start Guide

### 1. Run Backend Server & Seed Database
```bash
cd week36_analytics_dashboard/backend
python run.py
```
The Flask server seeds 1,000+ realistic demo events across 30 days and starts on `http://127.0.0.1:5000`.

### 2. Open Frontend Web Dashboard
Open the file in your web browser:
```
week36_analytics_dashboard/frontend/public/index.html
```

### 3. Run Automated Pytest Test Suite
```bash
cd week36_analytics_dashboard/backend
python -m pytest tests/ -v
```

### 4. Send a Sample Telemetry Event via cURL
```bash
curl -X POST http://127.0.0.1:5000/api/events \
  -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0" \
  -d '{
    "event_name": "pageview",
    "session_id": "sess_demo_101",
    "url_path": "/pricing",
    "country": "United States",
    "metadata": { "campaign": "product_hunt" }
  }'
```

---

## 🧪 Pytest Suite Status

- **Total Tests**: `126/126` passing across 8 specialized test modules.
- **Coverage**: Telemetry ingestion, UA/browser/OS parsers, time-series bucketing math, bounce rates, period comparison deltas, conversion funnels, CSV/JSON exports, SQL injection resilience, and REST controllers.
