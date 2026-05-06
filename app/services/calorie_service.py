# app/services/calorie_service.py
from app.database import get_db
from app.models import CalorieLog, UserProfile
from app.constants import MEAL_TYPES, MSG_INVALID_MEAL_TYPE


def get_user_profile(user_id):
    """Get user profile from database."""
    db = get_db()
    row = db.execute(
        "SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)
    ).fetchone()
    return UserProfile.from_row(row)


def log_calories(user_id, calories, meal_type, recipe_id=None):
    """Log a calorie entry for the user."""
    if meal_type not in MEAL_TYPES:
        raise ValueError(MSG_INVALID_MEAL_TYPE)

    db = get_db()
    db.execute(
        """INSERT INTO calorie_logs (user_id, recipe_id, calories, meal_type)
           VALUES (?, ?, ?, ?)""",
        (user_id, recipe_id, calories, meal_type)
    )
    db.commit()


def get_daily_summary(user_id, date):
    """Get total calories consumed for a specific date."""
    db = get_db()
    row = db.execute(
        """SELECT COALESCE(SUM(calories), 0) as total
           FROM calorie_logs
           WHERE user_id = ? AND date = ?""",
        (user_id, date)
    ).fetchone()
    return float(row["total"])


def get_remaining_calories(user_id, date):
    """Get remaining calories for the day."""
    profile = get_user_profile(user_id)
    if profile is None:
        return 0
    consumed = get_daily_summary(user_id, date)
    return profile.daily_calorie_goal - consumed


def get_calorie_history(user_id):
    """Get all calorie logs for a user."""
    db = get_db()
    rows = db.execute(
        """SELECT * FROM calorie_logs
           WHERE user_id = ?
           ORDER BY date DESC, id DESC""",
        (user_id,)
    ).fetchall()
    return [CalorieLog.from_row(row) for row in rows]