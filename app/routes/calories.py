# app/routes/calories.py
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.routes.auth import login_required
from app.services.calorie_service import (
    log_calories, get_daily_summary, get_remaining_calories,
    get_calorie_history, get_user_profile
)
from app.services.food_entry_factory import FoodEntryFactory
from app.constants import (
    MEAL_TYPES, ENTRY_SIMPLE, ENTRY_MACRO,
    FLASH_SUCCESS, FLASH_ERROR,
    MSG_CALORIES_LOGGED, MSG_MISSING_FIELDS,
    SESSION_USER_ID
)

calories_bp = Blueprint("calories", __name__)


@calories_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session[SESSION_USER_ID]
    today = date.today().isoformat()

    profile = get_user_profile(user_id)
    daily_total = get_daily_summary(user_id, today)
    remaining = get_remaining_calories(user_id, today)
    history = get_calorie_history(user_id)

    return render_template(
        "calories/dashboard.html",
        profile=profile,
        daily_total=daily_total,
        remaining=remaining,
        history=history,
        meal_types=MEAL_TYPES,
        today=today
    )


@calories_bp.route("/calories/log", methods=["POST"])
@login_required
def log():
    user_id = session[SESSION_USER_ID]
    meal_type = request.form.get("meal_type", "").strip()
    entry_type = request.form.get("entry_type", "simple").strip()

    if not meal_type:
        flash(MSG_MISSING_FIELDS, FLASH_ERROR)
        return redirect(url_for("calories.dashboard"))

    try:
        if entry_type == ENTRY_SIMPLE:
            calories_val = request.form.get("calories", "").strip()
            if not calories_val:
                flash(MSG_MISSING_FIELDS, FLASH_ERROR)
                return redirect(url_for("calories.dashboard"))
            entry = FoodEntryFactory.create(ENTRY_SIMPLE, calories=calories_val)
        else:
            protein = request.form.get("protein", "").strip()
            carbs = request.form.get("carbs", "").strip()
            fat = request.form.get("fat", "").strip()
            if not all([protein, carbs, fat]):
                flash(MSG_MISSING_FIELDS, FLASH_ERROR)
                return redirect(url_for("calories.dashboard"))
            entry = FoodEntryFactory.create(
                ENTRY_MACRO, protein=protein, carbs=carbs, fat=fat
            )

        log_calories(user_id, entry.get_calories(), meal_type)
        flash(MSG_CALORIES_LOGGED, FLASH_SUCCESS)

    except ValueError as e:
        flash(str(e), FLASH_ERROR)

    return redirect(url_for("calories.dashboard"))


@calories_bp.route("/calories/history")
@login_required
def history():
    user_id = session[SESSION_USER_ID]
    logs = get_calorie_history(user_id)
    return render_template("calories/history.html", logs=logs)