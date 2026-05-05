"""
tests/test_recipes.py
Recipe Tests — Ceyda Susal

Run with:
    pytest --cov=app tests/test_recipes.py -v
"""

import pytest
import json
import os
from app.database import get_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """Create and configure a Flask app instance for testing."""
    os.environ["SECRET_KEY"] = "test-secret-key"

    from app import create_app
    app = create_app()

    app.config["DATABASE"] = ":memory:"
    app.config["TESTING"] = True

    with app.app_context():
        from app.database import init_db
        init_db()
        _seed_test_data(app)

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(app):
    """A logged-in test client."""
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["email"] = "test@example.com"
        sess["name"] = "Test User"
    return client


# ---------------------------------------------------------------------------
# Seed helper
# ---------------------------------------------------------------------------

def _seed_test_data(app):
    from werkzeug.security import generate_password_hash
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
            ("test@example.com", generate_password_hash("password123"), "Test User"),
        )
        db.execute(
            "INSERT INTO recipes (title, ingredients, calorie_amount, budget, creator_id) VALUES (?, ?, ?, ?, ?)",
            ("Zucchini Pasta", json.dumps([{"name": "zucchini", "amount": "200g"}]), 450.0, 25.0, 1),
        )
        db.execute(
            "INSERT INTO recipes (title, ingredients, calorie_amount, budget, creator_id) VALUES (?, ?, ?, ?, ?)",
            ("Grilled Chicken", json.dumps([{"name": "chicken breast", "amount": "300g"}]), 320.0, 60.0, 1),
        )
        db.commit()


# ---------------------------------------------------------------------------
# Test 1 — Create a recipe
# ---------------------------------------------------------------------------

class TestCreateRecipe:
    def test_create_recipe_returns_new_id(self, app):
        from app.services.recipe_service import create_recipe
        with app.app_context():
            new_id = create_recipe("Egg Salad", [{"name": "egg", "amount": "2"}], 200.0, 10.0, 1)
        assert isinstance(new_id, int)
        assert new_id > 0

    def test_created_recipe_is_retrievable(self, app):
        from app.services.recipe_service import create_recipe, get_recipe_by_id
        with app.app_context():
            new_id = create_recipe("Tomato Soup", [{"name": "tomato", "amount": "400g"}], 150.0, 15.0, 1)
            recipe = get_recipe_by_id(new_id)
        assert recipe is not None
        assert recipe["title"] == "Tomato Soup"


# ---------------------------------------------------------------------------
# Test 2 — List all recipes
# ---------------------------------------------------------------------------

class TestListRecipes:
    def test_returns_all_seeded_recipes(self, app):
        from app.services.recipe_service import get_all_recipes
        with app.app_context():
            recipes = get_all_recipes()
        assert len(recipes) == 2

    def test_ingredients_are_decoded_as_list(self, app):
        from app.services.recipe_service import get_all_recipes
        with app.app_context():
            recipes = get_all_recipes()
        for recipe in recipes:
            assert isinstance(recipe["ingredients"], list)


# ---------------------------------------------------------------------------
# Test 3 — Filter by budget
# ---------------------------------------------------------------------------

class TestFilterByBudget:
    def test_budget_filter_excludes_expensive_recipes(self, app):
        from app.services.recipe_service import get_all_recipes
        with app.app_context():
            recipes = get_all_recipes(filter_budget=30.0)
        assert len(recipes) == 1
        assert recipes[0]["title"] == "Zucchini Pasta"

    def test_budget_filter_includes_all_when_high(self, app):
        from app.services.recipe_service import get_all_recipes
        with app.app_context():
            recipes = get_all_recipes(filter_budget=1000.0)
        assert len(recipes) == 2


# ---------------------------------------------------------------------------
# Test 4 — Filter by calories
# ---------------------------------------------------------------------------

class TestFilterByCalories:
    def test_calorie_filter_excludes_high_calorie_recipes(self, app):
        from app.services.recipe_service import get_all_recipes
        with app.app_context():
            recipes = get_all_recipes(filter_max_cal=400.0)
        assert len(recipes) == 1
        assert recipes[0]["title"] == "Grilled Chicken"

    def test_combined_budget_and_calorie_filter(self, app):
        from app.services.recipe_service import get_all_recipes
        with app.app_context():
            recipes = get_all_recipes(filter_budget=30.0, filter_max_cal=400.0)
        assert len(recipes) == 0


# ---------------------------------------------------------------------------
# Test 5 — Get recipe by id
# ---------------------------------------------------------------------------

class TestGetRecipeById:
    def test_returns_correct_recipe(self, app):
        from app.services.recipe_service import get_recipe_by_id
        with app.app_context():
            recipe = get_recipe_by_id(1)
        assert recipe is not None
        assert recipe["title"] == "Zucchini Pasta"

    def test_returns_none_for_missing_id(self, app):
        from app.services.recipe_service import get_recipe_by_id
        with app.app_context():
            recipe = get_recipe_by_id(9999)
        assert recipe is None


# ---------------------------------------------------------------------------
# Test 6 — Search recipes
# ---------------------------------------------------------------------------

class TestSearchRecipes:
    def test_search_finds_matching_title(self, app):
        from app.services.recipe_service import search_recipes
        with app.app_context():
            results = search_recipes("pasta")
        assert len(results) == 1
        assert results[0]["title"] == "Zucchini Pasta"

    def test_search_case_insensitive(self, app):
        from app.services.recipe_service import search_recipes
        with app.app_context():
            results = search_recipes("CHICKEN")
        assert len(results) == 1
        assert results[0]["title"] == "Grilled Chicken"

    def test_search_no_match_returns_empty(self, app):
        from app.services.recipe_service import search_recipes
        with app.app_context():
            results = search_recipes("xyz_no_match_xyz")
        assert results == []


# ---------------------------------------------------------------------------
# Route-level smoke tests
# ---------------------------------------------------------------------------

class TestRecipeRoutes:
    def test_list_page_returns_200(self, client):
        response = client.get("/recipes/")
        assert response.status_code == 200

    def test_detail_page_returns_200_for_existing(self, client):
        response = client.get("/recipes/1")
        assert response.status_code == 200

    def test_detail_page_redirects_for_missing(self, client):
        response = client.get("/recipes/9999")
        assert response.status_code == 302

    def test_create_page_redirects_when_not_logged_in(self, client):
        response = client.get("/recipes/create")
        assert response.status_code == 302

    def test_create_page_accessible_when_logged_in(self, auth_client):
        response = auth_client.get("/recipes/create")
        assert response.status_code == 200

    def test_create_post_creates_recipe_and_redirects(self, auth_client):
        response = auth_client.post("/recipes/create", data={
            "title": "Test Salad",
            "calories": "300",
            "budget": "20",
            "ingredient_name[]": ["lettuce"],
            "ingredient_amount[]": ["100g"],
        })
        assert response.status_code == 302

    def test_search_route_returns_200(self, client):
        response = client.get("/recipes/search?q=pasta")
        assert response.status_code == 200
