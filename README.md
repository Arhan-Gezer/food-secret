# Food Secret

A Flask-based web application for **recipe sharing**, **calorie tracking**, and **food ordering** - all in one place.

**Live demo:** https://food-secret-production.up.railway.app

**Final project for Software Engineering course (Yasar University, Spring 2026).**

---

## Features

| Module | Description | Status |
|--------|-------------|--------|
| Authentication | Register, login, logout with secure password hashing | Implemented |
| Recipes | Browse and share recipes with the community | In progress |
| Calorie Tracking | Log meals with simple/macro modes (Factory Pattern) | Implemented |
| Orders | Place orders for recipes from a chosen restaurant | Implemented |

---

## Tech Stack

- **Backend:** Python 3.12 + Flask 3.0
- **Database:** SQLite (raw SQL via the `sqlite3` module)
- **Templates:** Jinja2
- **Production server:** Gunicorn
- **Containerization:** Docker (`python:3.12-slim` base)
- **CI/CD:** GitHub Actions (test + lint pipeline)
- **Deployment:** Railway (auto-deploy via GitHub integration)
- **Testing:** pytest + pytest-cov

---

## Quick Start (Local)

### Prerequisites
- Python 3.12+
- Git
- Docker (optional, only for containerized run)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/Arhan-Gezer/food-secret.git
cd food-secret

# 2. Create and activate a virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
# Copy .env.example to .env and set:
#   SECRET_KEY=any-random-string
#   DATABASE=instance/food_secret.db

# 5. Initialize the database
flask --app run.py init-db

# 6. Run the development server
python run.py
```

Open `http://localhost:5000` and visit `/register` to create an account.

---

## Run with Docker

```bash
# Build the image
docker build -t food-secret .

# Run the container
docker run -p 5000:5000 -e SECRET_KEY=dev-key food-secret
```

The Dockerfile uses `python:3.12-slim` as the base, installs dependencies, runs `flask init-db` on container startup, and serves the app via gunicorn with 2 workers.

---

## Testing

The project uses **pytest** with **pytest-cov** for coverage reporting.

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing
```

### Test stats (current)
- 27 tests across 4 test files
- 25 passing (auth, orders, calories partial, smoke)
- Service-layer coverage: 100% for orders, 77% for auth, 72% for calories

---

## CI/CD Pipeline

GitHub Actions runs the test pipeline on every push:

```yaml
# .github/workflows/pipeline.yml
- Lint with flake8 (syntax errors fail the build)
- Run pytest with coverage
- (On push to main) Deploy to Railway
```

Deployment to Railway happens automatically on push to `develop` via Railway's GitHub integration. The `main` branch is reserved for production releases.

---

## Project Structure
---
```
food-secret/
  app/
    __init__.py             # Application factory (create_app)
    constants.py            # Shared string constants
    database.py             # SQLite connection + init_db
    models.py               # Data classes (User, Recipe, Order)
    routes/
      auth.py               # Register, login, logout
      recipes.py            # Recipe CRUD (in progress)
      calories.py           # Calorie logging dashboard
      orders.py             # Place orders, view history
    services/
      calorie_service.py
      food_entry_factory.py # Factory Pattern implementation
      order_service.py
    templates/              # Jinja2 templates per module
  tests/
    conftest.py             # Shared pytest fixtures
    test_auth.py
    test_calories.py
    test_orders.py
    test_smoke.py
  static/css/style.css
  .github/workflows/pipeline.yml
  Dockerfile
  .dockerignore
  requirements.txt
  run.py
  README.md
```

---

## Team

| Member | Module | Responsibilities |
|--------|--------|------------------|
| Arhan Gezer | Authentication, Project Setup | `app/__init__.py`, `models.py`, `database.py`, auth routes & tests |
| Erol Yuksel | Orders, DevOps | `services/order_service.py`, orders routes, Docker, CI/CD pipeline, Railway deployment |
| Cihan | Calorie Tracking | `calorie_service.py`, Factory Pattern food entries, calorie tests |
| Ceyda | Recipes | Recipe browse, create, share |

---

## License

This project is part of an academic assignment and is not licensed for commercial use.
