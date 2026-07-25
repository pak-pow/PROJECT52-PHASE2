"""
Week 30 — Social Feed Database Seeder
Drops and recreates all tables, then inserts demo users, bios, follows, posts, replies, and likes.
Run from: week30_social_feed/backend/
  python data/seed.py
"""
import sys
import os

# Allow importing the app package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db, init_db
from app.models.user_model import create_user, update_user_profile
from app.models.post_model import create_post, toggle_repost
from app.models.like_model import toggle_like
from app.models.follow_model import toggle_follow


def drop_all(conn):
    """Drop all tables in correct dependency order."""
    tables = ["reposts", "likes", "follows", "sessions", "posts", "users"]
    for table in tables:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    print("[OK] Dropped all tables.")


def seed():
    print("--- Week 30 Seeder ---------------------------------")

    # 1. Drop & recreate
    conn = get_db()
    drop_all(conn)
    conn.close()
    init_db()
    print("[OK] Schema initialised.")

    # 2. Create demo users with rich bios
    users_data = [
        ("alice",   "Alice Nguyen",   "password123", "Full-stack developer building 52 projects in 52 weeks 🚀 #buildinpublic"),
        ("bob",     "Bob Tanaka",     "password123", "Indie hacker & minimal UI enthusiast ☕ #webdev"),
        ("charlie", "Charlie Reyes",  "password123", "Python & Flask architect 🐍 #python"),
        ("diana",   "Diana Park",     "password123", "Frontend engineer & CSS wizard ✨ #design"),
        ("elena",   "Elena Rostova",  "password123", "UX designer & accessibility advocate 🎨 #uiux"),
        ("frank",   "Frank Miller",   "password123", "Backend dev & database optimization nerd ⚡ #sqlite"),
        ("grace",   "Grace Hopper",   "password123", "Software pioneer & bug hunter 🐞 #tech"),
        ("hannah",  "Hannah Lee",     "password123", "Open source contributor & tech blogger ✍️ #opensource"),
    ]

    user_ids = {}
    for username, display_name, password, bio in users_data:
        uid = create_user(username, display_name, password)
        user_ids[username] = uid
        update_user_profile(uid, display_name=display_name, bio=bio)
        print(f"  + user: @{username} (id={uid}) — '{display_name}'")

    # 3. Follows graph
    follow_pairs = [
        ("alice", "bob"), ("alice", "charlie"), ("alice", "diana"), ("alice", "elena"),
        ("bob", "alice"), ("bob", "diana"), ("bob", "frank"),
        ("charlie", "alice"), ("charlie", "frank"), ("charlie", "grace"),
        ("diana", "alice"), ("diana", "elena"), ("diana", "hannah"),
        ("elena", "alice"), ("elena", "diana"),
        ("frank", "bob"), ("frank", "charlie"),
        ("grace", "alice"), ("grace", "charlie"),
        ("hannah", "diana"), ("hannah", "elena")
    ]
    for follower, following in follow_pairs:
        toggle_follow(user_ids[follower], user_ids[following])
    print("[OK] Created " + str(len(follow_pairs)) + " follow relationships.")

    # 4. Posts
    posts_list = [
        ("alice",   "Just shipped Week 30 of Project52! Social feed is alive 🚀 #buildinpublic #webdev"),
        ("alice",   "Hot take: SQLite is underrated for personal projects. Fast, zero config, serverless. #sqlite"),
        ("bob",     "Morning coffee + dark mode feed = perfect combo ☕ #indiedev"),
        ("bob",     "Anyone else find infinite scroll weirdly satisfying to implement? #frontend"),
        ("charlie", "Day 1 of Week 30 and the scaffold is already looking clean 🔥 #python"),
        ("charlie", "Flask app factory pattern is so elegant. Blueprints make everything tidy. #backend"),
        ("diana",   "Just followed @alice — loving the Week 30 social feed dev updates! #design"),
        ("diana",   "The like toggle with optimistic UI is such a smooth UX pattern. #uiux"),
        ("elena",   "Accessibility tip: Always test your web app using keyboard navigation only. #a11y"),
        ("elena",   "Color contrast matters! Clean dark mode palettes make reading effortless. 🎨"),
        ("frank",   "WAL mode in SQLite enables concurrent readers while writing. Game changer for web apps! ⚡ #sqlite"),
        ("frank",   "Indexed queries cut response times from 120ms to 2ms. Never skip database indexes. 📊"),
        ("grace",   "The most dangerous phrase in the language is 'We've always done it this way.' 💡 #tech"),
        ("grace",   "Unit tests are not optional; they are your safety net when refactoring complex modules. 🐞"),
        ("hannah",  "Writing clean documentation is just as important as writing clean code. ✍️ #opensource"),
        ("hannah",  "Open source thrives when developers welcome beginners with open arms. ❤️"),
        ("alice",   "Building in public keeps you accountable and connects you with amazing indie builders! #buildinpublic"),
        ("bob",     "Flask + SQLite + Vanilla JS — the holy trinity of indie web development! 🌟"),
        ("charlie", "Python 3.12 performance improvements make Flask apps feel snappier than ever! ⚡"),
        ("diana",   "CSS Grid + Flexbox combined can construct virtually any layout with zero framework bloat. 🎨")
    ]

    post_ids = []
    for username, content in posts_list:
        pid = create_post(user_ids[username], content)
        post_ids.append(pid)
        print(f"  + post #{pid} by @{username}")

    # 5. Replies (threaded conversation)
    replies_data = [
        ("charlie", post_ids[0], "Replying to @alice — congratulations on reaching Week 30! 🎉"),
        ("diana",   post_ids[0], "Huge accomplishment! The UI looks super smooth ✨"),
        ("bob",     post_ids[1], "100% agreed! SQLite handles thousands of reads per second effortlessly."),
        ("frank",   post_ids[1], "Combined with WAL mode, SQLite is unbeatable for small to mid-sized web apps."),
        ("elena",   post_ids[6], "Welcome @diana! SocialFeed dev community is growing fast 🚀"),
        ("grace",   post_ids[10], "Spot on @frank! Concurrency in SQLite is often misunderstood.")
    ]
    for username, target_id, content in replies_data:
        rid = create_post(user_ids[username], content, reply_to_id=target_id)
        print(f"  + reply #{rid} by @{username} to post #{target_id}")

    # 6. Likes
    like_pairs = [
        ("bob", post_ids[0]), ("charlie", post_ids[0]), ("diana", post_ids[0]), ("elena", post_ids[0]), ("frank", post_ids[0]),
        ("alice", post_ids[2]), ("diana", post_ids[2]), ("hannah", post_ids[2]),
        ("alice", post_ids[4]), ("bob", post_ids[4]), ("grace", post_ids[4]),
        ("alice", post_ids[10]), ("charlie", post_ids[10]), ("grace", post_ids[10]),
        ("bob", post_ids[17]), ("charlie", post_ids[17]), ("diana", post_ids[17]), ("elena", post_ids[17]), ("frank", post_ids[17])
    ]
    for username, pid in like_pairs:
        toggle_like(user_ids[username], pid)
    print("[OK] Created " + str(len(like_pairs)) + " likes.")

    # 7. Reposts
    repost_pairs = [
        ("bob", post_ids[0]),
        ("diana", post_ids[0]),
        ("alice", post_ids[10]),
        ("charlie", post_ids[17])
    ]
    for username, pid in repost_pairs:
        toggle_repost(user_ids[username], pid)
    print("[OK] Created " + str(len(repost_pairs)) + " reposts.")

    print("--- Seeding complete! -----------------------------------")
    print("  Created 8 users, 26 posts & replies, 19 likes, 4 reposts, 21 follows.")
    print("  Login credentials: any username (alice, bob, charlie, diana, elena, etc.) / password123")


if __name__ == "__main__":
    seed()
