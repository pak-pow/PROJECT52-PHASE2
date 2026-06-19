from app.utils import db


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def insert_recipe(title: str, description: str, ingredients: str,
                  instructions: str, image_filename: str = None,
                  category: str = 'Uncategorised') -> dict:  # type: ignore
    conn = db.get_db()
    cursor = conn.execute(
        """
        INSERT INTO recipes (title, description, ingredients, instructions, image_filename, category)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (title, description, ingredients, instructions, image_filename, category)
    )
    conn.commit()
    return get_recipe_by_id(cursor.lastrowid)  # type: ignore


# ---------------------------------------------------------------------------
# Read — single
# ---------------------------------------------------------------------------

def get_recipe_by_id(recipe_id: int) -> dict:  # type: ignore
    """Returns a single recipe dict, or None if not found."""
    conn = db.get_db()
    row = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Read — list (paginated, with optional category + search filters)
# ---------------------------------------------------------------------------

def _build_filter_clause(category: str = None, search: str = None):
    """Returns (WHERE clause string, params tuple) for optional filters."""
    conditions, params = [], []
    if category and category.lower() != 'all':
        conditions.append("category = ?")
        params.append(category)
    if search:
        like = f"%{search}%"
        conditions.append("(title LIKE ? OR description LIKE ?)")
        params.extend([like, like])
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return where, params


def get_recipes_paginated(limit: int, offset: int,
                           category: str = None, search: str = None) -> list:
    """Fetches a page of recipes with optional category/search filters."""
    conn  = db.get_db()
    where, params = _build_filter_clause(category, search)
    sql   = f"SELECT * FROM recipes {where} ORDER BY created_at DESC LIMIT ? OFFSET ?"
    rows  = conn.execute(sql, (*params, limit, offset)).fetchall()
    return [dict(r) for r in rows]


def get_recipe_count(category: str = None, search: str = None) -> int:
    """Returns the total number of recipes matching the optional filters."""
    conn  = db.get_db()
    where, params = _build_filter_clause(category, search)
    row   = conn.execute(f"SELECT COUNT(*) FROM recipes {where}", params).fetchone()
    return row[0]


def get_all_recipes() -> list:
    """Fetches ALL recipes ordered newest first (unpaginated — used internally)."""
    conn = db.get_db()
    rows = conn.execute("SELECT * FROM recipes ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Read — categories
# ---------------------------------------------------------------------------

def get_all_categories() -> list:
    """Returns a sorted list of distinct categories that have at least one recipe."""
    conn = db.get_db()
    rows = conn.execute(
        "SELECT DISTINCT category FROM recipes WHERE category IS NOT NULL ORDER BY category"
    ).fetchall()
    return [r[0] for r in rows]


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_recipe(recipe_id: int, title: str, description: str,
                  ingredients: str, instructions: str,
                  image_filename=None, category: str = None) -> dict:  # type: ignore
    """
    Updates a recipe. If image_filename is provided the old image is replaced.
    If category is None the existing category is preserved.
    """
    conn = db.get_db()

    if image_filename is not None and category is not None:
        conn.execute(
            "UPDATE recipes SET title=?, description=?, ingredients=?, instructions=?, image_filename=?, category=? WHERE id=?",
            (title, description, ingredients, instructions, image_filename, category, recipe_id)
        )
    elif image_filename is not None:
        conn.execute(
            "UPDATE recipes SET title=?, description=?, ingredients=?, instructions=?, image_filename=? WHERE id=?",
            (title, description, ingredients, instructions, image_filename, recipe_id)
        )
    elif category is not None:
        conn.execute(
            "UPDATE recipes SET title=?, description=?, ingredients=?, instructions=?, category=? WHERE id=?",
            (title, description, ingredients, instructions, category, recipe_id)
        )
    else:
        conn.execute(
            "UPDATE recipes SET title=?, description=?, ingredients=?, instructions=? WHERE id=?",
            (title, description, ingredients, instructions, recipe_id)
        )

    conn.commit()
    return get_recipe_by_id(recipe_id)


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_recipe(recipe_id: int) -> bool:  # type: ignore
    conn    = db.get_db()
    cursor  = conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    conn.commit()
    return cursor.rowcount > 0