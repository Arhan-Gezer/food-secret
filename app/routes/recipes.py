"""
routes/recipes.py
Recipe Routes — Ceyda Susal

Blueprint: "recipes"
All routes here are prefixed with /recipes (registered in app/__init__.py).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.recipe_service import (
    create_recipe,
    get_all_recipes,
    get_recipe_by_id,
    search_recipes,
)
from app.constants import (
    FLASH_SUCCESS,
    FLASH_ERROR,
    MSG_RECIPE_NOT_FOUND,
    MSG_MISSING_FIELDS,
    MSG_RECIPE_CREATED,
    MSG_NOT_LOGGED_IN,
    SESSION_USER_ID,
)

recipes_bp = Blueprint("recipes", __name__, url_prefix="/recipes")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _login_required():
    """Return True if the user is logged in, else flash and redirect to login."""
    if SESSION_USER_ID not in session:
        flash(MSG_NOT_LOGGED_IN, FLASH_ERROR)
        return False
    return True


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@recipes_bp.route("/", methods=["GET"])
def list_recipes():
    """
    GET /recipes
    Show all recipes, with optional budget and calorie filters via query params.
    e.g. /recipes?budget=50&max_cal=600
    """
    filter_budget  = request.args.get("budget",  type=float)
    filter_max_cal = request.args.get("max_cal", type=float)

    recipes = get_all_recipes(filter_budget=filter_budget, filter_max_cal=filter_max_cal)

    return render_template(
        "recipes/list.html",
        recipes=recipes,
        filter_budget=filter_budget,
        filter_max_cal=filter_max_cal,
    )


@recipes_bp.route("/<int:recipe_id>", methods=["GET"])
def recipe_detail(recipe_id: int):
    """
    GET /recipes/<id>
    Show a single recipe's details.
    """
    recipe = get_recipe_by_id(recipe_id)
    if recipe is None:
        flash(MSG_RECIPE_NOT_FOUND, FLASH_ERROR)
        return redirect(url_for("recipes.list_recipes"))

    return render_template("recipes/detail.html", recipe=recipe)


@recipes_bp.route("/create", methods=["GET", "POST"])
def create_recipe_view():
    """
    GET  /recipes/create — show the creation form
    POST /recipes/create — handle form submission
    """
    if not _login_required():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        title    = request.form.get("title", "").strip()
        calories = request.form.get("calories", "").strip()
        budget   = request.form.get("budget",   "").strip()

        # Build ingredients list from repeating form fields
        # The form sends ingredient_name[] and ingredient_amount[]
        names   = request.form.getlist("ingredient_name[]")
        amounts = request.form.getlist("ingredient_amount[]")
        ingredients = [
            {"name": n.strip(), "amount": a.strip()}
            for n, a in zip(names, amounts)
            if n.strip()
        ]

        if not title or not calories or not budget:
            flash(MSG_MISSING_FIELDS, FLASH_ERROR)
            return render_template("recipes/create.html")

        try:
            calories = float(calories)
            budget   = float(budget)
        except ValueError:
            flash("Calories and budget must be numbers.", FLASH_ERROR)
            return render_template("recipes/create.html")

        creator_id = session[SESSION_USER_ID]
        create_recipe(title, ingredients, calories, budget, creator_id)
        flash(MSG_RECIPE_CREATED, FLASH_SUCCESS)
        return redirect(url_for("recipes.list_recipes"))

    return render_template("recipes/create.html")


@recipes_bp.route("/search", methods=["GET"])
def search():
    """
    GET /recipes/search?q=<query>
    Return recipes whose title matches the search string.
    """
    query = request.args.get("q", "").strip()
    results = search_recipes(query) if query else []

    return render_template("recipes/list.html", recipes=results, search_query=query)
