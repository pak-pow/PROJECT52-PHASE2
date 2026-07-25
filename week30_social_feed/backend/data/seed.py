"""
Week 30 — Social Feed Database Seeder
Drops and recreates all tables, then inserts demo users, avatars, follows, posts with sample images, replies, and likes.
Run from: week30_social_feed/backend/
  python data/seed.py
"""
import sys
import os

# Allow importing the app package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import Config
from app.db import get_db, init_db
from app.models.user_model import create_user, update_user_profile
from app.models.post_model import create_post, toggle_repost
from app.models.like_model import toggle_like
from app.models.follow_model import toggle_follow

try:
    from PIL import Image, ImageDraw  # type: ignore
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


def drop_all(conn):
    """Drop all tables in correct dependency order."""
    conn.execute("PRAGMA foreign_keys = OFF;")
    tables = ["reposts", "likes", "follows", "sessions", "posts", "users"]
    for table in tables:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON;")
    print("[OK] Dropped all tables.")


def generate_sample_images():
    """Generate sample avatars and post images in upload directories."""
    os.makedirs(Config.AVATAR_DIR, exist_ok=True)
    os.makedirs(Config.POST_IMAGE_DIR, exist_ok=True)

    if not PILLOW_AVAILABLE:
        return {}, []

    user_colors = {
        "alice":   "#6366f1",
        "bob":     "#ec4899",
        "charlie": "#10b981",
        "diana":   "#f59e0b",
        "elena":   "#8b5cf6",
        "frank":   "#3b82f6",
        "grace":   "#14b8a6",
        "hannah":  "#f43f5e",
    }

    # Generate User Avatars
    avatar_paths = {}
    for username, color in user_colors.items():
        filename = f"{username}_avatar.jpg"
        filepath = os.path.join(Config.AVATAR_DIR, filename)
        img = Image.new("RGB", (200, 200), color=color)
        draw = ImageDraw.Draw(img)
        initial = username[0].upper()
        draw.text((100, 100), initial, fill="#ffffff", anchor="mm")
        img.save(filepath, "JPEG", quality=90)
        avatar_paths[username] = filename

    # Generate Sample Post Images
    post_images_info = [
        ("sample_scenery.jpg", "#1e1b4b", "#4338ca", "Week 30 SocialFeed 🚀"),
        ("sample_code.jpg",    "#0f172a", "#334155", "Python + Flask + SQLite 🐍"),
        ("sample_design.jpg",  "#831843", "#be185d", "UI Design System ✨"),
        ("sample_setup.jpg",   "#064e3b", "#047857", "Developer Workspace ☕"),
    ]
    sample_post_img_paths = []
    for filename, col1, col2, label in post_images_info:
        filepath = os.path.join(Config.POST_IMAGE_DIR, filename)
        img = Image.new("RGB", (800, 500), color=col1)
        draw = ImageDraw.Draw(img)
        draw.rectangle([40, 40, 760, 460], outline=col2, width=6)
        draw.text((400, 250), label, fill="#ffffff", anchor="mm")
        img.save(filepath, "JPEG", quality=90)
        sample_post_img_paths.append(filename)

    return avatar_paths, sample_post_img_paths


def seed():
    print("--- Week 30 Seeder ---------------------------------")

    # 1. Drop & recreate
    conn = get_db()
    drop_all(conn)
    conn.close()
    init_db()
    print("[OK] Schema initialised.")

    # Generate images
    avatar_paths, sample_post_img_paths = generate_sample_images()

    # 2. Create demo users with rich bios and avatars
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
        av_path = avatar_paths.get(username)
        update_user_profile(uid, display_name=display_name, bio=bio, avatar_path=av_path)
        print("  + user: @" + username + " (id=" + str(uid) + ") - " + display_name)

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

    # 4. Posts (with sample images attached to specific posts)
    posts_list = [
        ("alice",   "Just shipped Week 30 of Project52! Social feed is alive 🚀 #buildinpublic #webdev", 0),
        ("alice",   "Hot take: SQLite is underrated for personal projects. Fast, zero config, serverless. #sqlite", None),
        ("bob",     "Morning coffee + dark mode feed = perfect combo ☕ #indiedev", 3),
        ("bob",     "Anyone else find infinite scroll weirdly satisfying to implement? #frontend", None),
        ("charlie", "Day 1 of Week 30 and the scaffold is already looking clean 🔥 #python", 1),
        ("charlie", "Flask app factory pattern is so elegant. Blueprints make everything tidy. #backend", None),
        ("diana",   "Just followed @alice — loving the Week 30 social feed dev updates! #design", 2),
        ("diana",   "The like toggle with optimistic UI is such a smooth UX pattern. #uiux", None),
        ("elena",   "Accessibility tip: Always test your web app using keyboard navigation only. #a11y", None),
        ("elena",   "Color contrast matters! Clean dark mode palettes make reading effortless. 🎨", None),
        ("frank",   "WAL mode in SQLite enables concurrent readers while writing. Game changer for web apps! ⚡ #sqlite", None),
        ("frank",   "Indexed queries cut response times from 120ms to 2ms. Never skip database indexes. 📊", None),
        ("grace",   "The most dangerous phrase in the language is 'We've always done it this way.' 💡 #tech", None),
        ("grace",   "Unit tests are not optional; they are your safety net when refactoring complex modules. 🐞", None),
        ("hannah",  "Writing clean documentation is just as important as writing clean code. ✍️ #opensource", None),
        ("hannah",  "Open source thrives when developers welcome beginners with open arms. ❤️", None),
        ("alice",   "Building in public keeps you accountable and connects you with amazing indie builders! #buildinpublic", None),
        ("bob",     "Flask + SQLite + Vanilla JS — the holy trinity of indie web development! 🌟", None),
        ("charlie", "Python 3.12 performance improvements make Flask apps feel snappier than ever! ⚡", None),
        ("diana",   "CSS Grid + Flexbox combined can construct virtually any layout with zero framework bloat. 🎨", None)
    ]

    post_ids = []
    for username, content, img_idx in posts_list:
        img_path = sample_post_img_paths[img_idx] if img_idx is not None and img_idx < len(sample_post_img_paths) else None
        pid = create_post(user_ids[username], content, image_path=img_path)
        post_ids.append(pid)
        print("  + post #" + str(pid) + " by @" + username + (" (with image)" if img_path else ""))

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
        print("  + reply #" + str(rid) + " by @" + username + " to post #" + str(target_id))

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
    print("  Created 8 users with avatars, 26 posts & replies (with images), 19 likes, 4 reposts, 21 follows.")
    print("  Login credentials: any username (alice, bob, charlie, diana, elena, etc.) / password123")


if __name__ == "__main__":
    seed()
