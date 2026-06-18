from app.utils import db


def insert_recipe(title: str, description: str, ingredients: str, instructions: str, image_filename: str = None) -> dict:  # type: ignore
    conn = db.get_db()
    cursor = conn.execute(
        """
        INSERT INTO recipes (title, description, ingredients, instructions, image_filename)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, description, ingredients, instructions, image_filename)
    )
    conn.commit()
    new_id = cursor.lastrowid
    return get_recipe_by_id(new_id)  # type: ignore


def get_recipe_by_id(recipe_id: int) -> dict:  # type: ignore
    """Returns a single recipe dict, or None if not found."""
    conn = db.get_db()
    cursor = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
    row = cursor.fetchone()
    return dict(row) if row else None  # Fixed: was dict(row) which crashes when row is None


def get_all_recipes() -> list:
    """Fetches all recipes, ordered by newest first."""
    conn = db.get_db()
    cursor = conn.execute("SELECT * FROM recipes ORDER BY created_at DESC")
    return [dict(row) for row in cursor.fetchall()]


def get_recipes_paginated(limit: int, offset: int) -> list:
    """Fetches a page of recipes, ordered by newest first."""
    conn = db.get_db()
    cursor = conn.execute(
        "SELECT * FROM recipes ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    )
    return [dict(row) for row in cursor.fetchall()]


def get_recipe_count() -> int:
    """Returns the total number of recipes in the database."""
    conn = db.get_db()
    cursor = conn.execute("SELECT COUNT(*) FROM recipes")
    return cursor.fetchone()[0]


def update_recipe(recipe_id: int, title: str, description: str, ingredients: str, instructions: str, image_filename=None, clear_image: bool = False) -> dict:  # type: ignore
    """
    Updates a recipe's fields. If image_filename is provided it replaces the old one.
    If clear_image is True the image is set to NULL (old file must be deleted by the caller).
    """
    conn = db.get_db()

    if image_filename is not None:
        # A new image was uploaded — replace regardless
        conn.execute(
            """
            UPDATE recipes
            SET title = ?, description = ?, ingredients = ?, instructions = ?, image_filename = ?
            WHERE id = ?
            """,
            (title, description, ingredients, instructions, image_filename, recipe_id)
        )
    elif clear_image:
        conn.execute(
            """
            UPDATE recipes
            SET title = ?, description = ?, ingredients = ?, instructions = ?, image_filename = NULL
            WHERE id = ?
            """,
            (title, description, ingredients, instructions, recipe_id)
        )
    else:
        # Keep existing image_filename untouched
        conn.execute(
            """
            UPDATE recipes
            SET title = ?, description = ?, ingredients = ?, instructions = ?
            WHERE id = ?
            """,
            (title, description, ingredients, instructions, recipe_id)
        )

    conn.commit()
    return get_recipe_by_id(recipe_id)


def delete_recipe(recipe_id: int) -> bool:  # type: ignore
    conn = db.get_db()
    cursor = conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    conn.commit()
    return cursor.rowcount > 0