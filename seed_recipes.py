import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import get_db

recipes = [
    {
        "title": "Spaghetti Carbonara",
        "calorie_amount": 620,
        "budget": 85.0,
        "ingredients": [
            {"name": "Spaghetti", "amount": "200g"},
            {"name": "Bacon", "amount": "100g"},
            {"name": "Egg", "amount": "2 adet"},
            {"name": "Parmesan", "amount": "50g"},
            {"name": "Black pepper", "amount": "1 tsp"},
        ]
    },
    {
        "title": "Tavuk Şiş",
        "calorie_amount": 480,
        "budget": 120.0,
        "ingredients": [
            {"name": "Chicken breast", "amount": "300g"},
            {"name": "Yogurt", "amount": "100ml"},
            {"name": "Tomato paste", "amount": "1 tbsp"},
            {"name": "Cumin", "amount": "1 tsp"},
            {"name": "Paprika", "amount": "1 tsp"},
        ]
    },
    {
        "title": "Avocado Toast",
        "calorie_amount": 320,
        "budget": 60.0,
        "ingredients": [
            {"name": "Sourdough bread", "amount": "2 slice"},
            {"name": "Avocado", "amount": "1 adet"},
            {"name": "Lemon juice", "amount": "1 tbsp"},
            {"name": "Red pepper flakes", "amount": "pinch"},
            {"name": "Salt", "amount": "to taste"},
        ]
    },
    {
        "title": "Mercimek Çorbası",
        "calorie_amount": 280,
        "budget": 35.0,
        "ingredients": [
            {"name": "Red lentils", "amount": "200g"},
            {"name": "Onion", "amount": "1 adet"},
            {"name": "Carrot", "amount": "1 adet"},
            {"name": "Cumin", "amount": "1 tsp"},
            {"name": "Butter", "amount": "1 tbsp"},
        ]
    },
    {
        "title": "Caesar Salad",
        "calorie_amount": 350,
        "budget": 75.0,
        "ingredients": [
            {"name": "Romaine lettuce", "amount": "1 baş"},
            {"name": "Parmesan", "amount": "40g"},
            {"name": "Croutons", "amount": "50g"},
            {"name": "Caesar dressing", "amount": "3 tbsp"},
            {"name": "Chicken breast", "amount": "150g"},
        ]
    },
    {
        "title": "Menemen",
        "calorie_amount": 310,
        "budget": 40.0,
        "ingredients": [
            {"name": "Egg", "amount": "3 adet"},
            {"name": "Tomato", "amount": "2 adet"},
            {"name": "Green pepper", "amount": "2 adet"},
            {"name": "Olive oil", "amount": "2 tbsp"},
            {"name": "Salt & pepper", "amount": "to taste"},
        ]
    },
    {
        "title": "Chicken Tikka Masala",
        "calorie_amount": 550,
        "budget": 140.0,
        "ingredients": [
            {"name": "Chicken breast", "amount": "350g"},
            {"name": "Tomato sauce", "amount": "200ml"},
            {"name": "Heavy cream", "amount": "100ml"},
            {"name": "Garam masala", "amount": "2 tsp"},
            {"name": "Garlic", "amount": "3 clove"},
        ]
    },
    {
        "title": "Falafel Wrap",
        "calorie_amount": 430,
        "budget": 55.0,
        "ingredients": [
            {"name": "Falafel", "amount": "6 adet"},
            {"name": "Lavash", "amount": "1 adet"},
            {"name": "Hummus", "amount": "3 tbsp"},
            {"name": "Tomato", "amount": "1 adet"},
            {"name": "Cucumber", "amount": "half"},
        ]
    },
    {
        "title": "İmam Bayıldı",
        "calorie_amount": 390,
        "budget": 50.0,
        "ingredients": [
            {"name": "Eggplant", "amount": "2 adet"},
            {"name": "Onion", "amount": "2 adet"},
            {"name": "Tomato", "amount": "3 adet"},
            {"name": "Garlic", "amount": "4 clove"},
            {"name": "Olive oil", "amount": "4 tbsp"},
        ]
    },
    {
        "title": "Salmon Teriyaki",
        "calorie_amount": 510,
        "budget": 180.0,
        "ingredients": [
            {"name": "Salmon fillet", "amount": "200g"},
            {"name": "Soy sauce", "amount": "3 tbsp"},
            {"name": "Honey", "amount": "2 tbsp"},
            {"name": "Ginger", "amount": "1 tsp"},
            {"name": "Sesame seeds", "amount": "1 tsp"},
        ]
    },
    {
        "title": "Kıymalı Makarna",
        "calorie_amount": 580,
        "budget": 70.0,
        "ingredients": [
            {"name": "Pasta", "amount": "200g"},
            {"name": "Ground beef", "amount": "200g"},
            {"name": "Tomato paste", "amount": "2 tbsp"},
            {"name": "Onion", "amount": "1 adet"},
            {"name": "Olive oil", "amount": "2 tbsp"},
        ]
    },
    {
        "title": "Greek Salad",
        "calorie_amount": 260,
        "budget": 65.0,
        "ingredients": [
            {"name": "Tomato", "amount": "2 adet"},
            {"name": "Cucumber", "amount": "1 adet"},
            {"name": "Feta cheese", "amount": "80g"},
            {"name": "Kalamata olives", "amount": "50g"},
            {"name": "Olive oil", "amount": "2 tbsp"},
        ]
    },
    {
        "title": "Pad Thai",
        "calorie_amount": 540,
        "budget": 95.0,
        "ingredients": [
            {"name": "Rice noodles", "amount": "150g"},
            {"name": "Shrimp", "amount": "150g"},
            {"name": "Egg", "amount": "2 adet"},
            {"name": "Peanuts", "amount": "30g"},
            {"name": "Fish sauce", "amount": "2 tbsp"},
        ]
    },
    {
        "title": "Lahmacun",
        "calorie_amount": 420,
        "budget": 45.0,
        "ingredients": [
            {"name": "Thin dough", "amount": "2 adet"},
            {"name": "Ground beef", "amount": "150g"},
            {"name": "Onion", "amount": "1 adet"},
            {"name": "Tomato", "amount": "1 adet"},
            {"name": "Parsley", "amount": "handful"},
        ]
    },
    {
        "title": "Shakshuka",
        "calorie_amount": 340,
        "budget": 50.0,
        "ingredients": [
            {"name": "Egg", "amount": "3 adet"},
            {"name": "Canned tomatoes", "amount": "400g"},
            {"name": "Red pepper", "amount": "1 adet"},
            {"name": "Cumin", "amount": "1 tsp"},
            {"name": "Feta cheese", "amount": "50g"},
        ]
    },
    {
        "title": "Burger",
        "calorie_amount": 700,
        "budget": 110.0,
        "ingredients": [
            {"name": "Ground beef patty", "amount": "200g"},
            {"name": "Burger bun", "amount": "1 adet"},
            {"name": "Cheddar cheese", "amount": "1 slice"},
            {"name": "Lettuce & tomato", "amount": "to taste"},
            {"name": "Sauce", "amount": "2 tbsp"},
        ]
    },
    {
        "title": "Mısır Çorbası",
        "calorie_amount": 250,
        "budget": 30.0,
        "ingredients": [
            {"name": "Sweet corn", "amount": "200g"},
            {"name": "Milk", "amount": "200ml"},
            {"name": "Butter", "amount": "1 tbsp"},
            {"name": "Flour", "amount": "1 tbsp"},
            {"name": "Salt & pepper", "amount": "to taste"},
        ]
    },
    {
        "title": "Tofu Stir Fry",
        "calorie_amount": 370,
        "budget": 80.0,
        "ingredients": [
            {"name": "Firm tofu", "amount": "200g"},
            {"name": "Broccoli", "amount": "150g"},
            {"name": "Soy sauce", "amount": "3 tbsp"},
            {"name": "Sesame oil", "amount": "1 tbsp"},
            {"name": "Garlic", "amount": "2 clove"},
        ]
    },
]


def seed():
    app = create_app()
    with app.app_context():
        db = get_db()

        # Get first user as creator
        user = db.execute("SELECT id FROM users LIMIT 1").fetchone()
        if not user:
            print("❌ No users found. Please register first, then run this script.")
            return

        creator_id = user["id"]
        count = 0

        for r in recipes:
            ingredients_json = json.dumps(r["ingredients"])
            db.execute(
                """INSERT INTO recipes (title, ingredients, calorie_amount, budget, creator_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (r["title"], ingredients_json, r["calorie_amount"], r["budget"], creator_id)
            )
            count += 1

        db.commit()
        print(f"✅ {count} recipes added successfully!")


if __name__ == "__main__":
    seed()
