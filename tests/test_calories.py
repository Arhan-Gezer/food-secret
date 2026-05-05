# tests/test_calories.py
import pytest
from app import create_app
from app.database import init_db
from app.services.food_entry_factory import FoodEntryFactory, SimpleFoodEntry, MacroFoodEntry
from app.services.calorie_service import log_calories, get_daily_summary, get_remaining_calories
from app.constants import ENTRY_SIMPLE, ENTRY_MACRO


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE": ":memory:",
    })
    with app.app_context():
        init_db()
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


def register_and_login(client):
    client.post("/register", data={
        "name": "Test User",
        "email": "test@test.com",
        "password": "123456",
        "weight": "70",
        "height": "175",
        "target_weight": "65",
        "age": "25",
        "gender": "male"
    })
    client.post("/login", data={
        "email": "test@test.com",
        "password": "123456"
    })


# --- Factory Tests ---

def test_simple_food_entry():
    entry = FoodEntryFactory.create(ENTRY_SIMPLE, calories=500)
    assert isinstance(entry, SimpleFoodEntry)
    assert entry.get_calories() == 500.0


def test_macro_food_entry():
    entry = FoodEntryFactory.create(ENTRY_MACRO, protein=30, carbs=50, fat=10)
    assert isinstance(entry, MacroFoodEntry)
    # 30*4 + 50*4 + 10*9 = 120 + 200 + 90 = 410
    assert entry.get_calories() == 410.0


def test_factory_invalid_type():
    with pytest.raises(ValueError):
        FoodEntryFactory.create("invalid_type", calories=100)


def test_simple_entry_zero_calories():
    entry = FoodEntryFactory.create(ENTRY_SIMPLE, calories=0)
    assert entry.get_calories() == 0.0


def test_macro_entry_zero_values():
    entry = FoodEntryFactory.create(ENTRY_MACRO, protein=0, carbs=0, fat=0)
    assert entry.get_calories() == 0.0


# --- Calorie Service Tests ---

def test_log_calories_success(app):
    from app.database import get_db
    db = get_db()
    db.execute(
        "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
        ("test@test.com", "hash", "Test User")
    )
    db.execute(
        """INSERT INTO user_profiles
           (user_id, weight, height, target_weight, age, gender, daily_calorie_goal)
           VALUES (1, 70, 175, 65, 25, 'male', 1724)"""
    )
    db.commit()
    log_calories(1, 500, "breakfast")
    total = get_daily_summary(1, __import__("datetime").date.today().isoformat())
    assert total == 500.0


def test_get_daily_summary_empty(app):
    total = get_daily_summary(999, "2026-01-01")
    assert total == 0.0


def test_get_remaining_calories(app):
    from app.database import get_db
    db = get_db()
    db.execute(
        "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
        ("test2@test.com", "hash", "Test User 2")
    )
    db.execute(
        """INSERT INTO user_profiles
           (user_id, weight, height, target_weight, age, gender, daily_calorie_goal)
           VALUES (1, 70, 175, 65, 25, 'male', 2000)"""
    )
    db.commit()
    log_calories(1, 500, "breakfast")
    today = __import__("datetime").date.today().isoformat()
    remaining = get_remaining_calories(1, today)
    assert remaining == 1500.0

# --- Route Tests ---

def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302


def test_dashboard_accessible_when_logged_in(client):
    register_and_login(client)
    response = client.get("/dashboard")
    assert response.status_code == 200


def test_log_calories_route(client):
    register_and_login(client)
    response = client.post("/calories/log", data={
        "meal_type": "breakfast",
        "entry_type": "simple",
        "calories": "500"
    })
    assert response.status_code == 302


def test_log_calories_macro_route(client):
    register_and_login(client)
    response = client.post("/calories/log", data={
        "meal_type": "lunch",
        "entry_type": "macro",
        "protein": "30",
        "carbs": "50",
        "fat": "10"
    })
    assert response.status_code == 302