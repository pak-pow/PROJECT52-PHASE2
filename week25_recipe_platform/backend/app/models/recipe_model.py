from app.utils import db

def insert_recipe(title: str, description: str, ingredients: str, instructions: str, image_filename: str = None) -> dict: # type: ignore
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
    return get_recipe_by_id(new_id) #type: ignore

def get_recipe_by_id(recipe_id: int) -> dict:
    conn = db.get_db()
    cursor = conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
    return dict(cursor.fetchone())

def get_all_recipes() -> list:
    """Fetches all recipes, ordered by newest first."""
    conn = db.get_db()
    cursor = conn.execute("SELECT * FROM recipes ORDER BY created_at DESC")
    
    # Convert the SQLite Row objects into a list of standard Python dictionaries
    return [dict(row) for row in cursor.fetchall()]