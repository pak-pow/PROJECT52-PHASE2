"""
Week 30 — Social Feed Database Seeder
Drops and recreates all tables, then inserts demo users, follows, posts, and likes.
Run from: week30_social_feed/backend/
  python data/seed.py
"""
import sys
import os

# Allow importing the app package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db, init_db
from app.models.user_model import create_user
from app.models.post_model import create_post
from app.models.like_model import toggle_like
from app.models.follow_model import toggle_follow


def drop_all(conn):
    """Drop all tables in correct dependency order."""
    tables = ["likes", "follows", "sessions", "posts", "users"]
    for table in tables:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    print("✓ Dropped all tables.")


def seed():
    print("── Week 30 Seeder ─────────────────────────────────")

    # 1. Drop & recreate
    conn = get_db()
    drop_all(conn)
    conn.close()
    init_db()
    print("✓ Schema initialised.")

    # 2. Create demo users
    users = [
        ("alice",   "Alice Nguyen",   "password123"),
        ("bob",     "Bob Tanaka",     "password123"),
        ("charlie", "Charlie Reyes",  "password123"),
        ("diana",   "Diana Park",     "password123"),
    ]
    user_ids = {}
    for username, display_name, password in users:
        uid = create_user(username, display_name, password)
        user_ids[username] = uid
        print(f"  + user: @{username} (id={uid})")

    # 3. Follows
    follow_pairs = [
        ("alice", "bob"),
        ("alice", "charlie"),
        ("bob",   "alice"),
        ("bob",   "diana"),
        ("charlie", "alice"),
        ("diana", "charlie"),
    ]
    for follower, following in follow_pairs:
        toggle_follow(user_ids[follower], user_ids[following])
    print(f"✓ Created {len(follow_pairs)} follow relationships.")

    # 4. Posts
    posts_data = [
        ("alice",   "Just shipped Week 30 of Project52! Social feed is alive 🚀 #buildinpublic"),
        ("alice",   "Hot take: SQLite is underrated for personal projects. Fast, zero config, serverless."),
        ("bob",     "Morning coffee + dark mode feed = perfect combo ☕"),
        ("bob",     "Anyone else find infinite scroll weirdly satisfying to implement?"),
        ("charlie", "Day 1 of Week 30 and the scaffold is already looking clean 🔥"),
        ("charlie", "Flask app factory pattern is so elegant. Blueprints make everything tidy."),
        ("diana",   "Just followed @alice — loving the Week 30 social feed dev updates!"),
        ("diana",   "The like toggle with optimistic UI is such a smooth UX pattern."),
        ("alice",   "Reply test incoming 👇"),
        ("bob",     "Flask + SQLite + Vanilla JS — the holy trinity of indie dev."),
    ]
    post_ids = []
    for username, content in posts_data:
        pid = create_post(user_ids[username], content)
        post_ids.append(pid)
        print(f"  + post #{pid} by @{username}")

    # 5. A reply
    reply_id = create_post(
        user_ids["charlie"],
        "Replying to @alice — this reply threading is already working beautifully!",
        reply_to_id=post_ids[8],  # reply to alice's "Reply test incoming" post
    )
    print(f"  + reply #{reply_id} by @charlie")

    # 6. Likes
    like_pairs = [
        ("bob",     post_ids[0]),
        ("charlie", post_ids[0]),
        ("diana",   post_ids[0]),
        ("alice",   post_ids[2]),
        ("diana",   post_ids[2]),
        ("alice",   post_ids[4]),
        ("bob",     post_ids[4]),
        ("alice",   post_ids[9]),
        ("charlie", post_ids[9]),
        ("diana",   post_ids[9]),
    ]
    for username, post_id in like_pairs:
        toggle_like(user_ids[username], post_id)
    print(f"✓ Created {len(like_pairs)} likes.")

    print("── Seeding complete! ───────────────────────────────")
    print("  Login credentials: any username above / password123")


if __name__ == "__main__":
    seed()
