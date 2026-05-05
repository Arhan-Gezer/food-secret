# models.py
import json
from app.constants import GENDER_MALE


class User:
    def __init__(self, id, email, password_hash, name):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.name = name

    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return User(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            name=row["name"]
        )


class UserProfile:
    def __init__(self, id, user_id, weight, height, target_weight,
                 age, gender, daily_calorie_goal):
        self.id = id
        self.user_id = user_id
        self.weight = weight
        self.height = height
        self.target_weight = target_weight
        self.age = age
        self.gender = gender
        self.daily_calorie_goal = daily_calorie_goal

    @staticmethod
    def calculate_bmr(weight, height, age, gender):
        if gender == GENDER_MALE:
            return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return UserProfile(
            id=row["id"],
            user_id=row["user_id"],
            weight=row["weight"],
            height=row["height"],
            target_weight=row["target_weight"],
            age=row["age"],
            gender=row["gender"],
            daily_calorie_goal=row["daily_calorie_goal"]
        )


class Recipe:
    def __init__(self, id, title, ingredients, calorie_amount,
                 budget, creator_id, created_at=None):
        self.id = id
        self.title = title
        self.ingredients = ingredients
        self.calorie_amount = calorie_amount
        self.budget = budget
        self.creator_id = creator_id
        self.created_at = created_at

    def get_ingredients_list(self):
        return json.loads(self.ingredients)

    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return Recipe(
            id=row["id"],
            title=row["title"],
            ingredients=row["ingredients"],
            calorie_amount=row["calorie_amount"],
            budget=row["budget"],
            creator_id=row["creator_id"],
            created_at=row["created_at"]
        )


class CalorieLog:
    def __init__(self, id, user_id, recipe_id, calories, meal_type, date):
        self.id = id
        self.user_id = user_id
        self.recipe_id = recipe_id
        self.calories = calories
        self.meal_type = meal_type
        self.date = date

    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return CalorieLog(
            id=row["id"],
            user_id=row["user_id"],
            recipe_id=row["recipe_id"],
            calories=row["calories"],
            meal_type=row["meal_type"],
            date=row["date"]
        )


class Order:
    def __init__(self, id, user_id, recipe_id, restaurant_name,
                 status, created_at=None):
        self.id = id
        self.user_id = user_id
        self.recipe_id = recipe_id
        self.restaurant_name = restaurant_name
        self.status = status
        self.created_at = created_at

    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return Order(
            id=row["id"],
            user_id=row["user_id"],
            recipe_id=row["recipe_id"],
            restaurant_name=row["restaurant_name"],
            status=row["status"],
            created_at=row["created_at"]
        )