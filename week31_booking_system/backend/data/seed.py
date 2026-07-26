"""
Week 31 — Booking & Appointment System Seeder
Drops and recreates all tables, then inserts demo users, providers, services, working hours, and sample bookings.
Run from: week31_booking_system/backend/
  python data/seed.py
"""
import sys
import os
import datetime
from werkzeug.security import generate_password_hash  # type: ignore

# Allow importing the app package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db, init_db


def drop_all(conn):
    """Drop all tables in dependency order."""
    conn.execute("PRAGMA foreign_keys = OFF;")
    tables = [
        "bookings",
        "provider_availability",
        "provider_services",
        "providers",
        "services",
        "sessions",
        "users",
    ]
    for table in tables:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON;")
    print("[OK] Dropped all tables.")


def seed():
    print("--- Week 31 Seeder ---------------------------------")

    conn = get_db()
    drop_all(conn)
    conn.close()

    init_db()
    conn = get_db()
    print("[OK] Schema initialised.")

    # 1. Create Users
    users_data = [
        ("alice",       "Alice Nguyen",     "alice@example.com",     "client",   "password123"),
        ("bob",         "Bob Tanaka",       "bob@example.com",       "client",   "password123"),
        ("dr_smith",    "Dr. Alex Smith",   "smith@example.com",     "provider", "password123"),
        ("dr_jones",    "Dr. Sarah Jones",  "jones@example.com",     "provider", "password123"),
        ("coach_mike",  "Mike Vance",       "mike@example.com",      "provider", "password123"),
        ("salon_elena", "Elena Rostova",    "elena@example.com",     "provider", "password123"),
    ]

    user_ids = {}
    for username, name, email, role, pwd in users_data:
        pwd_hash = generate_password_hash(pwd)
        cursor = conn.execute(
            "INSERT INTO users (username, display_name, email, role, password_hash) VALUES (?, ?, ?, ?, ?)",
            (username, name, email, role, pwd_hash)
        )
        user_ids[username] = cursor.lastrowid
        print("  + user: @" + username + " (" + role + ")")

    # 2. Create Providers
    providers_data = [
        ("dr_smith",    "Primary Care Physician",  "Specializing in family medicine, wellness exams, and preventative care."),
        ("dr_jones",    "Senior Dentist",          "Expert in restorative dentistry, teeth whitening, and hygiene."),
        ("coach_mike",  "Executive Coach",         "Helping professionals unlock potential, leadership, and performance."),
        ("salon_elena", "Master Stylist",          "Creative hair styling, coloring, and personal image design."),
    ]

    provider_ids = {}
    for username, title, bio in providers_data:
        uid = user_ids[username]
        cursor = conn.execute(
            "INSERT INTO providers (user_id, title, bio) VALUES (?, ?, ?)",
            (uid, title, bio)
        )
        provider_ids[username] = cursor.lastrowid
        print("  + provider: " + username + " (id=" + str(cursor.lastrowid) + ")")

    # 3. Create Services
    services_data = [
        ("General Medical Exam",        "Comprehensive wellness checkup and medical consultation.", 30, 75.0,  "Health"),
        ("Dental Checkup & Cleaning",   "Teeth cleaning, plaque removal, and oral health assessment.", 45, 120.0, "Dental"),
        ("Executive Career Coaching",   "1-on-1 career strategy and leadership consultation.", 60, 150.0, "Coaching"),
        ("Haircut & Styling Session",   "Precision haircut, shampoo, and custom styling.", 45, 60.0,  "Beauty"),
        ("Express Health Check",        "Quick 15-minute prescription renewal or blood pressure check.", 15, 40.0,  "Health"),
    ]

    service_ids = []
    for title, desc, duration, price, category in services_data:
        cursor = conn.execute(
            "INSERT INTO services (title, description, duration_minutes, price, category) VALUES (?, ?, ?, ?, ?)",
            (title, desc, duration, price, category)
        )
        service_ids.append(cursor.lastrowid)
        print("  + service: " + title + " (" + str(duration) + "m, $" + str(price) + ")")

    # 4. Map Providers to Services
    mappings = [
        (provider_ids["dr_smith"],    service_ids[0]),
        (provider_ids["dr_smith"],    service_ids[4]),
        (provider_ids["dr_jones"],    service_ids[1]),
        (provider_ids["coach_mike"],  service_ids[2]),
        (provider_ids["salon_elena"], service_ids[3]),
    ]
    for pid, sid in mappings:
        conn.execute("INSERT INTO provider_services (provider_id, service_id) VALUES (?, ?)", (pid, sid))
    print("[OK] Mapped providers to services.")

    # 5. Set Provider Availability (Monday to Friday, 09:00 to 17:00)
    for pid in provider_ids.values():
        for day in range(0, 5):  # 0=Mon ... 4=Fri
            conn.execute(
                "INSERT INTO provider_availability (provider_id, day_of_week, start_time, end_time) VALUES (?, ?, '09:00', '17:00')",
                (pid, day)
            )
    print("[OK] Created weekly working hours for providers (Mon-Fri 09:00-17:00).")

    # 6. Sample Initial Bookings for upcoming dates
    today = datetime.date.today()
    tomorrow = (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    next_week = (today + datetime.timedelta(days=3)).strftime("%Y-%m-%d")

    sample_bookings = [
        (user_ids["alice"], provider_ids["dr_smith"], service_ids[0], tomorrow, "10:00", "10:30", "Regular checkup"),
        (user_ids["bob"],   provider_ids["dr_jones"], service_ids[1], tomorrow, "11:00", "11:45", "Routine dental cleaning"),
        (user_ids["alice"], provider_ids["coach_mike"], service_ids[2], next_week, "14:00", "15:00", "Career goal planning"),
    ]
    for uid, pid, sid, bdate, stime, etime, notes in sample_bookings:
        conn.execute(
            """INSERT INTO bookings (user_id, provider_id, service_id, booking_date, start_time, end_time, status, notes)
               VALUES (?, ?, ?, ?, ?, ?, 'confirmed', ?)""",
            (uid, pid, sid, bdate, stime, etime, notes)
        )
    print("[OK] Created sample initial appointments.")

    conn.commit()
    conn.close()

    print("--- Seeding complete! -----------------------------------")
    print("  Created 6 users, 4 service providers, 5 services, 3 initial bookings.")
    print("  Credentials: any username (alice, bob, dr_smith, dr_jones, coach_mike, salon_elena) / password123")


if __name__ == "__main__":
    seed()
