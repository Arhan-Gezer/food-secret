# tests/test_auth.py
import pytest
from app import create_app
from app.database import init_db


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


def test_register_success(client):
    response = client.post("/register", data={
        "name": "Test User",
        "email": "test@test.com",
        "password": "123456",
        "weight": "70",
        "height": "175",
        "target_weight": "65",
        "age": "25",
        "gender": "male"
    })
    assert response.status_code == 302


def test_register_duplicate_email(client):
    data = {
        "name": "Test User",
        "email": "test@test.com",
        "password": "123456",
        "weight": "70",
        "height": "175",
        "target_weight": "65",
        "age": "25",
        "gender": "male"
    }
    client.post("/register", data=data)
    response = client.post("/register", data=data)
    assert b"already registered" in response.data


def test_register_missing_fields(client):
    response = client.post("/register", data={
        "name": "",
        "email": "",
        "password": "",
        "weight": "",
        "height": "",
        "target_weight": "",
        "age": "",
        "gender": ""
    })
    assert b"fill in all required fields" in response.data


def test_login_success(client):
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
    response = client.post("/login", data={
        "email": "test@test.com",
        "password": "123456"
    })
    assert response.status_code == 302


def test_login_wrong_password(client):
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
    response = client.post("/login", data={
        "email": "test@test.com",
        "password": "wrongpassword"
    })
    assert b"Invalid email or password" in response.data


def test_login_wrong_email(client):
    response = client.post("/login", data={
        "email": "wrong@test.com",
        "password": "123456"
    })
    assert b"Invalid email or password" in response.data


def test_login_missing_fields(client):
    response = client.post("/login", data={
        "email": "",
        "password": ""
    })
    assert b"fill in all required fields" in response.data


def test_logout(client):
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
    response = client.get("/logout")
    assert response.status_code == 302