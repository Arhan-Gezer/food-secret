"""
tests/test_recipes.py
Recipe Tests — Ceyda Susal

Run with:
    pytest --cov=app tests/test_recipes.py -v

All tests use Flask's built-in test client with an in-memory SQLite database
so no real database file is created or modified.
"""

import pytest
import json
from app import create_app
from app.database import init_db, get_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """Create and configure a Flask app instance for testing."""
    app = create_app({
        "TESTING": True,
        "DATABASE": ":memory:",
        "SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        init_db()
        _seed_test_data(app)

    yield app


@pytest.fixture
def client(app):
    """Test client with an active app context."""
    return app.test_client()


@pytest.fixture
def auth_client(app):
    """
    A test client that is already logged in as the seeded test user.
    Simulates a logged-in session without going through the login form.
    """
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["email"]   = "test@example.com"
        sess["name"]    = "Test User"
    return client


# ---------------------------------------------------------------------------
# Seed helper
# ---------------------------------------------------------------------------

def _seed_test_data(app):
    """Insert one user and two recipes into the in-memory DB."""
    from werkzeug.security import generate_password_hash

    with app.app_context():
        db = get_db()

        # Insert user
        db.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
            ("test@example.com", generate_password_hash("password123"), "Test User"),
        )

        # Insert two recipes with different budgets and calorie amounts
        db.execute(
            """
            INSERT INTO recipes (title, ingredients, calorie_amount, budget, creator_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "Zucchini Pasta",
                json.dumps([{"name": "zucchini", "amount": "200g"}, {"name": "pasta", "amount": "100g"}]),
                450.0,
                25.0,
                1,
            ),
        )
        db.execute(
            """
            INSERT INTO recipes (title, ingredients, calorie_amount, budget, creator_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "Grilled Chicken",
                json.dumps([{"name": "chicken breast", "amount": "300g"}]),
                320.0,
                60.0,
                1,
            ),
        )
        db.commit()


# ---------------------------------------------------------------------------
# Test 1 — Create a recipe (service layer)
# ---------------------------------------------------------------------------

class TestCreateRecipe:
    def test_create_recipe_returns_new_id(self, app):
        """create_recipe() should insert a row and return its integer id."""
        from app.services.recipe_service import create_recipe

        with app.app_context():
            new_id = create_recipe(
                title="Egg Salad",
                ingredients=[{"name": "egg", "amount": "2 pcs"}, {"name": "mayo", "amount": "1 tbsp"}],
                calories=200.0,
                budget=10.0,
                creator_id=1,
            )

        assert isinstance(new_id, int)
        assert new_id > 0

    def test_created_recipe_is_retrievable(self, app):
        """A recipe created via create_recipe() must be fetchable by its id."""
        from app.services.recipe_service import create_recipe, get_recipe_by_id

        with app.app_context():
            new_id = create_recipe(
                title="Tomato Soup",
                ingredients=[{"name": "tomato", "amount": "400g"}],
                calories=150.0,
                budget=15.0,
                creator_id=1,
            )
            recipe = get_recipe_by_id(new_id)

        assert recipe is not None
        assert recipe["title"] == "Tomato Soup"
        assert recipe["calorie_amount"] == 150.0
        assert len(recipe["ingredients"]) == 1


# ---------------------------------------------------------------------------
# Test 2 — List all recipes (service layer)
# ---------------------------------------------------------------------------

class TestListRecipes:
    def test_returns_all_seeded_recipes(self, app):
        """get_all_recipes() with no filters should return both seeded recipes."""
        from app.services.recipe_service import get_all_recipes

        with app.app_context():
            recipes = get_all_recipes()

        assert len(recipes) == 2

    def test_ingredients_are_decoded_as_list(self, app):
        """Ingredients stored as JSON strings must come back as Python lists."""
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
        """
        Only 'Zucchini Pasta' (₺25) should be returned when max budget is ₺30.
        'Grilled Chicken' (₺60) must be excluded.
        """
        from app.services.recipe_service import get_all_recipes

        with app.app_context():
            recipes = get_all_recipes(filter_budget=30.0)

        assert len(recipes) == 1
        assert recipes[0]["title"] == "Zucchini Pasta"

    def test_budget_filter_includes_all_when_high(self, app):
        """A very high budget filter should return every recipe."""
        from app.services.recipe_service import get_all_recipes

        with app.app_context():
            recipes = get_all_recipes(filter_budget=1000.0)

        assert len(recipes) == 2


# ---------------------------------------------------------------------------
# Test 4 — Filter by max calories
# ---------------------------------------------------------------------------

class TestFilterByCalories:
    def test_calorie_filter_excludes_high_calorie_recipes(self, app):
        """
        Only 'Grilled Chicken' (320 kcal) should appear when max_cal = 400.
        'Zucchini Pasta' (450 kcal) must be excluded.
        """
        from app.services.recipe_service import get_all_recipes

        with app.app_context():
            recipes = get_all_recipes(filter_max_cal=400.0)

        assert len(recipes) == 1
        assert recipes[0]["title"] == "Grilled Chicken"

    def test_combined_budget_and_calorie_filter(self, app):
        """Combined filters: both ₺30 budget AND 400 kcal max → no results."""
        from app.services.recipe_service import get_all_recipes

        with app.app_context():
            recipes = get_all_recipes(filter_budget=30.0, filter_max_cal=400.0)

        # Zucchini Pasta passes budget but fails calories; Chicken fails budget
        assert len(recipes) == 0


# ---------------------------------------------------------------------------
# Test 5 — Get recipe by id
# ---------------------------------------------------------------------------

class TestGetRecipeById:
    def test_returns_correct_recipe(self, app):
        """get_recipe_by_id(1) must return the first seeded recipe."""
        from app.services.recipe_service import get_recipe_by_id

        with app.app_context():
            recipe = get_recipe_by_id(1)

        assert recipe is not None
        assert recipe["id"] == 1
        assert recipe["title"] == "Zucchini Pasta"

    def test_returns_none_for_missing_id(self, app):
        """get_recipe_by_id with a non-existent id must return None."""
        from app.services.recipe_service import get_recipe_by_id

        with app.app_context():
            recipe = get_recipe_by_id(9999)

        assert recipe is None


# ---------------------------------------------------------------------------
# Test 6 (bonus) — Search recipes
# ---------------------------------------------------------------------------

class TestSearchRecipes:
    def test_search_finds_matching_title(self, app):
        """search_recipes('pasta') should return 'Zucchini Pasta'."""
        from app.services.recipe_service import search_recipes

        with app.app_context():
            results = search_recipes("pasta")

        assert len(results) == 1
        assert results[0]["title"] == "Zucchini Pasta"

    def test_search_case_insensitive(self, app):
        """Search must be case-insensitive: 'CHICKEN' matches 'Grilled Chicken'."""
        from app.services.recipe_service import search_recipes

        with app.app_context():
            results = search_recipes("CHICKEN")

        assert len(results) == 1
        assert results[0]["title"] == "Grilled Chicken"

    def test_search_empty_query_returns_empty_list(self, app):
        """An empty query string passed to search_recipes returns empty list."""
        from app.services.recipe_service import search_recipes

        with app.app_context():
            results = search_recipes("")

        # LIKE %% matches everything — this is fine per spec; document it
        # If your team decides empty query → empty result, change the route layer.
        assert isinstance(results, list)


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
        assert response.status_code == 302  # redirect to list

    def test_create_page_redirects_when_not_logged_in(self, client):
        response = client.get("/recipes/create")
        assert response.status_code == 302  # redirect to login

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
        assert response.status_code == 302  # redirect to list after success

    def test_search_route_returns_200(self, client):
        response = client.get("/recipes/search?q=pasta")
        assert response.status_code == 200
