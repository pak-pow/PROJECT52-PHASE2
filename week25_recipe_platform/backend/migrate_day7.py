"""
Day 7 Migration: adds 'category' column to existing recipes table
and assigns categories to the seeded recipes.
Run once from the backend/ directory: python migrate_day7.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'database.db')

conn = sqlite3.connect(DB_PATH)

# Add column — silently skip if it already exists
try:
    conn.execute("ALTER TABLE recipes ADD COLUMN category TEXT DEFAULT 'Uncategorised'")
    conn.commit()
    print("Migration OK: 'category' column added.")
except Exception as e:
    print(f"Column already exists (OK): {e}")

# Assign categories to the originally seeded recipes
seed_categories = [
    (1, 'Dinner'),      # Classic Spaghetti Carbonara
    (2, 'Dinner'),      # Honey Garlic Butter Salmon
    (3, 'Lunch'),       # Smoky Black Bean Tacos
    (4, 'Breakfast'),   # Fluffy Japanese Pancakes
    (5, 'Soup'),        # One-Pot Tuscan White Bean Soup
    (6, 'Breakfast'),   # Pandesal
]
for recipe_id, category in seed_categories:
    conn.execute("UPDATE recipes SET category=? WHERE id=? AND (category IS NULL OR category='Uncategorised')",
                 (category, recipe_id))
conn.commit()

print("\nCategory assignments:")
rows = conn.execute("SELECT id, title, category FROM recipes ORDER BY id").fetchall()
for row in rows:
    print(f"  [{row[0]}] {row[1]:40s} -> {row[2]}")

conn.close()
print("\nDone.")
