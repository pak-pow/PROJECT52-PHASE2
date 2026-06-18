"""
Seed script: populates the recipes database with sample data.
Run from the backend/ directory:  python seed.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'database.db')

SAMPLE_RECIPES = [
    {
        "title": "Classic Spaghetti Carbonara",
        "description": "A rich and creamy Roman pasta dish made with eggs, Pecorino Romano, pancetta, and black pepper. No cream needed — the magic is all in the technique.",
        "ingredients": (
            "400g spaghetti\n"
            "200g pancetta or guanciale, diced\n"
            "4 large eggs\n"
            "100g Pecorino Romano, finely grated\n"
            "50g Parmesan, finely grated\n"
            "2 cloves garlic\n"
            "Salt and freshly cracked black pepper"
        ),
        "instructions": (
            "1. Bring a large pot of salted water to a boil and cook spaghetti until al dente.\n"
            "2. While pasta cooks, fry pancetta in a large skillet over medium heat until crispy. Remove garlic after 1 minute.\n"
            "3. In a bowl, whisk together eggs, Pecorino Romano, and Parmesan. Season generously with black pepper.\n"
            "4. Reserve 1 cup of pasta cooking water, then drain the pasta.\n"
            "5. Off the heat, add pasta to the skillet with pancetta. Pour egg mixture over the pasta, tossing quickly.\n"
            "6. Add pasta water a splash at a time to loosen into a silky sauce. Serve immediately."
        ),
        "image_filename": None,
    },
    {
        "title": "Honey Garlic Butter Salmon",
        "description": "Pan-seared salmon fillets glazed with a sticky honey garlic butter sauce. Ready in under 20 minutes and absolutely packed with flavour.",
        "ingredients": (
            "4 salmon fillets (about 180g each)\n"
            "3 tbsp unsalted butter\n"
            "4 cloves garlic, minced\n"
            "3 tbsp honey\n"
            "2 tbsp soy sauce\n"
            "1 tbsp lemon juice\n"
            "Salt, pepper, and fresh parsley to garnish"
        ),
        "instructions": (
            "1. Pat salmon dry and season both sides with salt and pepper.\n"
            "2. Heat 1 tbsp butter in a skillet over medium-high heat. Sear salmon skin-side up for 4 minutes.\n"
            "3. Flip and cook for another 3 minutes. Remove salmon and set aside.\n"
            "4. In the same pan, melt remaining butter. Add garlic and sauté for 30 seconds.\n"
            "5. Stir in honey, soy sauce, and lemon juice. Simmer for 2 minutes until slightly thickened.\n"
            "6. Return salmon to the pan and spoon glaze over the top. Garnish with parsley and serve."
        ),
        "image_filename": None,
    },
    {
        "title": "Smoky Black Bean Tacos",
        "description": "Hearty vegetarian tacos loaded with smoky spiced black beans, avocado crema, pickled red onion, and a squeeze of lime. A weeknight staple.",
        "ingredients": (
            "2 cans (400g each) black beans, drained\n"
            "1 tsp smoked paprika\n"
            "1 tsp cumin\n"
            "1/2 tsp chilli powder\n"
            "2 cloves garlic, minced\n"
            "8 small corn or flour tortillas\n"
            "2 ripe avocados\n"
            "1/2 cup sour cream\n"
            "1 red onion, thinly sliced\n"
            "2 tbsp apple cider vinegar\n"
            "Lime, fresh coriander, and hot sauce to serve"
        ),
        "instructions": (
            "1. Quick-pickle onion: toss sliced onion with vinegar and a pinch of salt. Set aside for 15 minutes.\n"
            "2. Heat oil in a pan, add garlic and spices, cook 30 seconds until fragrant.\n"
            "3. Add black beans and 1/4 cup water. Mash about half the beans and simmer 5 minutes until thickened.\n"
            "4. Make avocado crema: blend avocados with sour cream and a squeeze of lime until smooth.\n"
            "5. Warm tortillas in a dry pan or directly over a gas flame.\n"
            "6. Assemble tacos: beans, avocado crema, pickled onion, coriander, and hot sauce."
        ),
        "image_filename": None,
    },
    {
        "title": "Fluffy Japanese Pancakes",
        "description": "Impossibly thick, cloud-like soufflé pancakes with a jiggly texture. A breakfast showstopper that is easier to make than it looks.",
        "ingredients": (
            "2 large eggs, separated\n"
            "2 tbsp whole milk\n"
            "1/2 tsp vanilla extract\n"
            "3 tbsp plain flour\n"
            "1/2 tsp baking powder\n"
            "1 tbsp sugar\n"
            "Butter and oil for the pan\n"
            "Maple syrup and fresh berries to serve"
        ),
        "instructions": (
            "1. Mix egg yolks with milk and vanilla. Sift in flour and baking powder, stir until smooth.\n"
            "2. In a separate bowl, beat egg whites until foamy. Gradually add sugar and whip to stiff, glossy peaks.\n"
            "3. Gently fold the meringue into the yolk batter in two stages — do not deflate it.\n"
            "4. Heat a non-stick pan over the lowest heat possible. Lightly grease with butter.\n"
            "5. Spoon batter into two tall mounds (use a ring mould if you have one). Add a splash of water to the pan and cover immediately.\n"
            "6. Cook 4–5 minutes, flip carefully, cover and cook another 4 minutes. Serve with maple syrup and berries."
        ),
        "image_filename": None,
    },
    {
        "title": "One-Pot Tuscan White Bean Soup",
        "description": "A hearty, rustic Italian soup with cannellini beans, kale, tomatoes, and rosemary. Deeply satisfying and ready in 30 minutes.",
        "ingredients": (
            "2 cans (400g each) cannellini beans, drained\n"
            "1 can (400g) crushed tomatoes\n"
            "1 litre vegetable or chicken stock\n"
            "1 onion, diced\n"
            "4 cloves garlic, sliced\n"
            "150g kale or cavolo nero, roughly chopped\n"
            "1 sprig fresh rosemary\n"
            "2 tbsp olive oil\n"
            "Salt, pepper, and Parmesan rind (optional but highly recommended)\n"
            "Crusty bread to serve"
        ),
        "instructions": (
            "1. Heat olive oil in a large pot over medium heat. Sauté onion until softened, about 5 minutes.\n"
            "2. Add garlic and rosemary, cook for 1 minute until fragrant.\n"
            "3. Add crushed tomatoes and cook for 3 minutes, stirring occasionally.\n"
            "4. Pour in stock, add beans and Parmesan rind if using. Bring to a simmer.\n"
            "5. Add kale and cook for 10 minutes until tender. Remove rosemary sprig and Parmesan rind.\n"
            "6. Use a spoon to lightly crush some beans for a creamier texture. Season to taste and serve with crusty bread."
        ),
        "image_filename": None,
    },
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Idempotency guard: skip if already seeded
    existing = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    if existing > 0:
        print(f"Database already has {existing} recipe(s). Skipping seed to avoid duplicates.")
        conn.close()
        return

    inserted = 0
    for recipe in SAMPLE_RECIPES:
        conn.execute(
            """
            INSERT INTO recipes (title, description, ingredients, instructions, image_filename)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                recipe["title"],
                recipe["description"],
                recipe["ingredients"],
                recipe["instructions"],
                recipe["image_filename"],
            ),
        )
        inserted += 1
        print(f"  [OK] Inserted: {recipe['title']}")

    conn.commit()
    conn.close()
    print(f"\nDone -- {inserted} sample recipes added to {DB_PATH}")


if __name__ == "__main__":
    seed()
