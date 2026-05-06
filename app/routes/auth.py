# app/routes/auth.py
import functools
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db
from app.models import User, UserProfile
from app.constants import (
    SESSION_USER_ID, SESSION_EMAIL, SESSION_NAME,
    FLASH_SUCCESS, FLASH_ERROR,
    MSG_INVALID_CREDENTIALS, MSG_EMAIL_TAKEN, MSG_NOT_LOGGED_IN,
    MSG_REGISTER_SUCCESS, MSG_LOGIN_SUCCESS, MSG_LOGOUT_SUCCESS,
    MSG_MISSING_FIELDS, GENDERS
)

auth_bp = Blueprint("auth", __name__)


def login_required(view):
    """Redirect to login page if user is not logged in."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if SESSION_USER_ID not in session:
            flash(MSG_NOT_LOGGED_IN, FLASH_ERROR)
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        weight = request.form.get("weight", "").strip()
        height = request.form.get("height", "").strip()
        target_weight = request.form.get("target_weight", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()

        if not all([name, email, password, weight, height, target_weight, age, gender]):
            flash(MSG_MISSING_FIELDS, FLASH_ERROR)
            return render_template("auth/register.html", genders=GENDERS)
        
        try:
            weight_val = float(weight)
            height_val = float(height)
            target_weight_val = float(target_weight)
            age_val = int(age)
            if weight_val <= 0 or height_val <= 0 or target_weight_val <= 0 or age_val <= 0:
                flash("Please enter valid positive values.", FLASH_ERROR)
                return render_template("auth/register.html", genders=GENDERS)
        except ValueError:
            flash("Please enter valid numbers.", FLASH_ERROR)
            return render_template("auth/register.html", genders=GENDERS)

        db = get_db()

        existing_user = db.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()

        if existing_user:
            flash(MSG_EMAIL_TAKEN, FLASH_ERROR)
            return render_template("auth/register.html", genders=GENDERS)

        password_hash = generate_password_hash(password)

        db.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
            (email, password_hash, name)
        )
        db.commit()

        user = db.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()

        daily_calorie_goal = UserProfile.calculate_bmr(
            float(weight), float(height), int(age), gender
        )

        db.execute(
            """INSERT INTO user_profiles
               (user_id, weight, height, target_weight, age, gender, daily_calorie_goal)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user["id"], float(weight), float(height),
             float(target_weight), int(age), gender, daily_calorie_goal)
        )
        db.commit()

        flash(MSG_REGISTER_SUCCESS, FLASH_SUCCESS)
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", genders=GENDERS)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not all([email, password]):
            flash(MSG_MISSING_FIELDS, FLASH_ERROR)
            return render_template("auth/login.html")

        db = get_db()
        row = db.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        user = User.from_row(row)

        if user is None or not check_password_hash(user.password_hash, password):
            flash(MSG_INVALID_CREDENTIALS, FLASH_ERROR)
            return render_template("auth/login.html")

        session.clear()
        session[SESSION_USER_ID] = user.id
        session[SESSION_EMAIL] = user.email
        session[SESSION_NAME] = user.name

        flash(MSG_LOGIN_SUCCESS, FLASH_SUCCESS)
        return redirect(url_for("calories.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash(MSG_LOGOUT_SUCCESS, FLASH_SUCCESS)
    return redirect(url_for("auth.login"))

@auth_bp.route("/")
def index():
    if SESSION_USER_ID in session:
        return redirect(url_for("calories.dashboard"))
    return render_template("index.html")