"""
services/recipe_service.py
Recipe Management — Ceyda Susal

All recipe-related business logic lives here.
Routes import from here; routes never touch the DB directly.
"""

import json
from app.database import get_db


def create_recipe(title: str, ingredients: list, calories: float, budget: float, creator_id: int) -> int:
    """
    Insert a new recipe row and return its new id.

    Parameters
    ----------
    title       : recipe name
    ingredients : list of dicts  e.g. [{"name": "tavuk", "amount": "200g"}, ...]
    calories    : total calorie amount (kcal)
    budget      : estimated cost
    creator_id  : id of the logged-in user
    """
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO recipes (title, ingredients, calorie_amount, budget, creator_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, json.dumps(ingredients, ensure_ascii=False), calories, budget, creator_id),
    )
    db.commit()
    return cursor.lastrowid


def get_all_recipes(filter_budget: float = None, filter_max_cal: float = None) -> list:
    """
    Return all recipes, optionally filtered by max budget and/or max calories.

    Parameters
    ----------
    filter_budget  : keep recipes whose budget <= this value (None = no filter)
    filter_max_cal : keep recipes whose calorie_amount <= this value (None = no filter)
    """
    db = get_db()

    query = "SELECT * FROM recipes WHERE 1=1"
    params = []

    if filter_budget is not None:
        query += " AND budget <= ?"
        params.append(filter_budget)

    if filter_max_cal is not None:
        query += " AND calorie_amount <= ?"
        params.append(filter_max_cal)

    query += " ORDER BY created_at DESC"

    rows = db.execute(query, params).fetchall()
    return [_parse_recipe(row) for row in rows]


def get_recipe_by_id(recipe_id: int) -> dict | None:
    """
    Return a single recipe dict, or None if it does not exist.
    """
    db = get_db()
    row = db.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if row is None:
        return None
    return _parse_recipe(row)


def search_recipes(query: str) -> list:
    """
    Full-text search on recipe title (case-insensitive substring match).
    Returns a list of matching recipe dicts.
    """
    db = get_db()
    pattern = f"%{query}%"
    rows = db.execute(
        "SELECT * FROM recipes WHERE title LIKE ? ORDER BY created_at DESC",
        (pattern,),
    ).fetchall()
    return [_parse_recipe(row) for row in rows]


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _parse_recipe(row) -> dict:
    """Convert a sqlite3.Row to a plain dict and decode the ingredients JSON."""
    recipe = dict(row)
    try:
        recipe["ingredients"] = json.loads(recipe["ingredients"])
    except (json.JSONDecodeError, TypeError):
        recipe["ingredients"] = []
    return recipe
