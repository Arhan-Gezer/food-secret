# app/__init__.py
import os
from flask import Flask
from app import database


def create_app():
    app = Flask(__name__, instance_relative_config=True, static_folder='../static')

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),
        DATABASE=os.path.join(app.instance_path, "food_secret.db"),
    )

    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize database
    database.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.recipes import recipes_bp
    from app.routes.calories import calories_bp
    from app.routes.orders import orders_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(recipes_bp)
    app.register_blueprint(calories_bp)
    app.register_blueprint(orders_bp)

    return app