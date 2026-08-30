import os
import sys
import random
from datetime import datetime, timedelta

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import init_db, get_db_connection
from app.models.event_model import EventModel
from app.models.funnel_model import FunnelModel

def seed_database(num_events: int = 1000):
    print("[SEED] Initializing database schema...")
    init_db()

    print("[SEED] Creating Conversion Funnels...")
    FunnelModel.create_funnel(
        name="E-Commerce Purchase Funnel",
        description="Tracks visitor journey from landing page view to checkout purchase.",
        steps=[
            {"step_name": "Landing Page View", "event_name": "pageview"},
            {"step_name": "Product Click", "event_name": "click"},
            {"step_name": "User Signup", "event_name": "signup"},
            {"step_name": "Completed Purchase", "event_name": "purchase"}
        ]
    )

    FunnelModel.create_funnel(
        name="SaaS Lead Gen Funnel",
        description="Tracks visitor conversion from docs to account signup.",
        steps=[
            {"step_name": "View Documentation", "event_name": "pageview"},
            {"step_name": "Register Free Account", "event_name": "signup"}
        ]
    )

    print(f"[SEED] Generating {num_events} realistic telemetry events...")

    paths = [
        "/", "/dashboard", "/pricing", "/features", "/docs",
        "/blog/scale-python-apis", "/checkout", "/signup", "/contact",
        "/products/analytics-pro", "/products/enterprise-cloud"
    ]
    referrers = [
        "https://google.com", "https://twitter.com", "https://github.com",
        "https://linkedin.com", "https://news.ycombinator.com", None
    ]
    devices = [("desktop", 0.60), ("mobile", 0.35), ("tablet", 0.05)]
    browsers = [("Chrome", 0.55), ("Safari", 0.25), ("Firefox", 0.12), ("Edge", 0.08)]
    os_list = [("Windows", 0.45), ("MacOS", 0.30), ("iOS", 0.15), ("Android", 0.08), ("Linux", 0.02)]
    countries = [
        "United States", "United Kingdom", "Germany", "Japan",
        "Canada", "France", "Australia", "India", "Singapore"
    ]
    events_weights = [("pageview", 0.65), ("click", 0.20), ("signup", 0.10), ("purchase", 0.05)]

    def weighted_choice(choices_with_weights):
        items, weights = zip(*choices_with_weights)
        return random.choices(items, weights=weights, k=1)[0]

    now = datetime.utcnow()
    sessions = [f"sess_{random.randint(1000, 9999)}_{i}" for i in range(150)]

    for i in range(num_events):
        # Distribute events over the past 30 days
        days_ago = random.uniform(0, 30)
        event_time = now - timedelta(days=days_ago, minutes=random.randint(0, 1440))
        created_at_str = event_time.strftime("%Y-%m-%d %H:%M:%S")

        event_name = weighted_choice(events_weights)
        session_id = random.choice(sessions)
        url_path = random.choice(paths)
        referrer = random.choice(referrers)
        device = weighted_choice(devices)
        browser = weighted_choice(browsers)
        os_name = weighted_choice(os_list)
        country = random.choice(countries)
        user_id = f"usr_{random.randint(10, 80)}" if random.random() > 0.5 else None
        metadata = {"screen_res": "1920x1080", "latency_ms": random.randint(15, 120)}

        EventModel.create_event(
            event_name=event_name,
            session_id=session_id,
            url_path=url_path,
            user_id=user_id,
            referrer=referrer,
            device_type=device,
            browser=browser,
            os_name=os_name,
            country=country,
            metadata=metadata,
            created_at=created_at_str
        )

    print("[SEED] Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database(1000)
