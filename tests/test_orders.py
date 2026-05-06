# tests/test_orders.py
"""Tests for the orders module - service layer + route integration."""

from app.services import order_service
from app.constants import ORDER_PENDING, ORDER_CONFIRMED


def test_place_order_creates_pending(app, seed_user, seed_recipe):
    """A new order should be created with status='pending' by default."""
    with app.app_context():
        order_id = order_service.place_order(
            user_id=seed_user,
            recipe_id=seed_recipe,
            restaurant_name="Test Restaurant",
        )

        assert order_id is not None

        order = order_service.get_order_by_id(order_id, seed_user)
        assert order is not None
        assert order["status"] == ORDER_PENDING
        assert order["restaurant_name"] == "Test Restaurant"


def test_get_user_orders_returns_only_own(app, seed_user, seed_recipe):
    """Users must only see their own orders, never another user's."""
    with app.app_context():
        from app.database import get_db
        db = get_db()

        cursor = db.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
            ("other@test.com", "fake-hash", "Other User"),
        )
        db.commit()
        other_user_id = cursor.lastrowid

        order_service.place_order(seed_user, seed_recipe, "My Restaurant")
        order_service.place_order(other_user_id, seed_recipe, "Their Restaurant")

        my_orders = order_service.get_user_orders(seed_user)
        their_orders = order_service.get_user_orders(other_user_id)

        assert len(my_orders) == 1
        assert len(their_orders) == 1
        assert my_orders[0]["restaurant_name"] == "My Restaurant"
        assert their_orders[0]["restaurant_name"] == "Their Restaurant"


def test_place_order_returns_none_for_invalid_recipe(app, seed_user):
    """Trying to order a non-existent recipe must return None, not raise."""
    with app.app_context():
        result = order_service.place_order(
            user_id=seed_user,
            recipe_id=99999,
            restaurant_name="Ghost Restaurant",
        )
        assert result is None


def test_update_order_status_rejects_invalid_status(app, seed_user, seed_recipe):
    """Status updates must be validated against ORDER_STATUSES."""
    with app.app_context():
        order_id = order_service.place_order(seed_user, seed_recipe, "Test")

        # Invalid status should be rejected
        ok = order_service.update_order_status(order_id, seed_user, "banana")
        assert ok is False

        # Valid status should work
        ok = order_service.update_order_status(order_id, seed_user, ORDER_CONFIRMED)
        assert ok is True

        order = order_service.get_order_by_id(order_id, seed_user)
        assert order["status"] == ORDER_CONFIRMED


def test_orders_route_requires_login(client):
    """Accessing /orders/ without login must redirect to login page."""
    response = client.get("/orders/")
    assert response.status_code == 302
    assert "/login" in response.location