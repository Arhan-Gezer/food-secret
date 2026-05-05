# app/routes/orders.py
"""Order routes - handle HTTP requests for placing and viewing orders."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from app.routes.auth import login_required
from app.services import order_service
from app.constants import (
    SESSION_USER_ID,
    FLASH_SUCCESS, FLASH_ERROR,
    MSG_ORDER_PLACED, MSG_ORDER_NOT_FOUND, MSG_MISSING_FIELDS,
    ORDER_STATUSES,
)

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


@orders_bp.route("/", methods=["GET"])
@login_required
def history():
    """Show all orders placed by the current user."""
    user_id = session[SESSION_USER_ID]
    orders = order_service.get_user_orders(user_id)
    return render_template("orders/history.html", orders=orders)


@orders_bp.route("/place", methods=["POST"])
@login_required
def place():
    """Place a new order from a recipe page."""
    user_id = session[SESSION_USER_ID]

    recipe_id = request.form.get("recipe_id", "").strip()
    restaurant_name = request.form.get("restaurant_name", "").strip()

    if not recipe_id or not restaurant_name:
        flash(MSG_MISSING_FIELDS, FLASH_ERROR)
        return redirect(url_for("orders.history"))

    try:
        recipe_id_int = int(recipe_id)
    except ValueError:
        flash(MSG_MISSING_FIELDS, FLASH_ERROR)
        return redirect(url_for("orders.history"))

    new_id = order_service.place_order(user_id, recipe_id_int, restaurant_name)

    if new_id is None:
        flash(MSG_ORDER_NOT_FOUND, FLASH_ERROR)
        return redirect(url_for("orders.history"))

    flash(MSG_ORDER_PLACED, FLASH_SUCCESS)
    return redirect(url_for("orders.detail", order_id=new_id))


@orders_bp.route("/<int:order_id>", methods=["GET"])
@login_required
def detail(order_id):
    """Show a single order's details."""
    user_id = session[SESSION_USER_ID]
    order = order_service.get_order_by_id(order_id, user_id)

    if order is None:
        abort(404)

    return render_template(
        "orders/detail.html",
        order=order,
        statuses=ORDER_STATUSES,
    )


@orders_bp.route("/<int:order_id>/update", methods=["POST"])
@login_required
def update(order_id):
    """Update the status of an order (pending -> confirmed -> delivered)."""
    user_id = session[SESSION_USER_ID]
    new_status = request.form.get("status", "").strip()

    success = order_service.update_order_status(order_id, user_id, new_status)

    if not success:
        flash(MSG_ORDER_NOT_FOUND, FLASH_ERROR)
        return redirect(url_for("orders.history"))

    flash("Order status updated.", FLASH_SUCCESS)
    return redirect(url_for("orders.detail", order_id=order_id))