from app.database import get_db
from app.models import Recipe

def get_all_recipes():
    db = get_db()
    rows = db.execute("SELECT * FROM recipes").fetchall()

    recipes = []
    for row in rows:
        recipes.append(Recipe.from_row(row))

    return recipes