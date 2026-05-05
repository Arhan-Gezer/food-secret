# app/services/order_service.py
"""Order service - business logic for placing and managing orders."""

from app.database import get_db
from app.constants import ORDER_PENDING, ORDER_STATUSES


def place_order(user_id, recipe_id, restaurant_name):
    """Create a new order with status='pending'.
    Returns the new order's id, or None if recipe doesn't exist.
    """
    db = get_db()

    recipe = db.execute(
        "SELECT id FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()
    if recipe is None:
        return None

    cursor = db.execute(
        """INSERT INTO orders (user_id, recipe_id, restaurant_name, status)
           VALUES (?, ?, ?, ?)""",
        (user_id, recipe_id, restaurant_name, ORDER_PENDING)
    )
    db.commit()
    return cursor.lastrowid


def get_user_orders(user_id):
    """Return all orders belonging to a user, newest first."""
    db = get_db()
    rows = db.execute(
        """SELECT o.id, o.recipe_id, o.restaurant_name, o.status, o.created_at,
                  r.title AS recipe_title
           FROM orders o
           LEFT JOIN recipes r ON o.recipe_id = r.id
           WHERE o.user_id = ?
           ORDER BY o.created_at DESC""",
        (user_id,)
    ).fetchall()
    return rows


def get_order_by_id(order_id, user_id):
    """Return a single order, but only if it belongs to the given user.
    Returns None if not found or not owned by user.
    """
    db = get_db()
    row = db.execute(
        """SELECT o.id, o.user_id, o.recipe_id, o.restaurant_name, o.status, o.created_at,
                  r.title AS recipe_title
           FROM orders o
           LEFT JOIN recipes r ON o.recipe_id = r.id
           WHERE o.id = ? AND o.user_id = ?""",
        (order_id, user_id)
    ).fetchone()
    return row


def update_order_status(order_id, user_id, new_status):
    """Update an order's status. Returns True if updated, False otherwise.
    Validates that new_status is in ORDER_STATUSES and order belongs to user.
    """
    if new_status not in ORDER_STATUSES:
        return False

    db = get_db()
    cursor = db.execute(
        "UPDATE orders SET status = ? WHERE id = ? AND user_id = ?",
        (new_status, order_id, user_id)
    )
    db.commit()
    return cursor.rowcount > 0