# tests/conftest.py
"""Shared pytest fixtures for the test suite."""
import os
import tempfile

import pytest

from app import create_app
from app.database import init_db, get_db


@pytest.fixture
def app():
    """Create a fresh Flask app with a temporary database for each test."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        DATABASE=db_path,
        SECRET_KEY="test-secret-key",
        WTF_CSRF_ENABLED=False,
    )

    with flask_app.app_context():
        init_db()

    yield flask_app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Provide a Flask test client tied to the test app."""
    return app.test_client()


@pytest.fixture
def seed_user(app):
    """Insert a test user into the database and return their id."""
    with app.app_context():
        db = get_db()
        cursor = db.execute(
            "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
            ("test@test.com", "fake-hash", "Test User"),
        )
        db.commit()
        return cursor.lastrowid


@pytest.fixture
def seed_recipe(app, seed_user):
    """Insert a test recipe into the database and return its id."""
    with app.app_context():
        db = get_db()
        cursor = db.execute(
            """INSERT INTO recipes (title, ingredients, calorie_amount, budget, creator_id)
               VALUES (?, ?, ?, ?, ?)""",
            ("Test Pasta", "pasta, sauce", 450, 25, seed_user),
        )
        db.commit()
        return cursor.lastrowid


@pytest.fixture
def logged_in_client(client, seed_user):
    """A test client that has a logged-in session as seed_user."""
    with client.session_transaction() as sess:
        sess["user_id"] = seed_user
        sess["email"] = "test@test.com"
        sess["name"] = "Test User"
    return client