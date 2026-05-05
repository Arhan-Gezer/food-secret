# database.py
import sqlite3
import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            name          TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_profiles (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id             INTEGER NOT NULL UNIQUE,
            weight              REAL    NOT NULL,
            height              REAL    NOT NULL,
            target_weight       REAL    NOT NULL,
            age                 INTEGER NOT NULL,
            gender              TEXT    NOT NULL,
            daily_calorie_goal  REAL    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS recipes (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            title          TEXT    NOT NULL,
            ingredients    TEXT    NOT NULL,
            calorie_amount REAL    NOT NULL,
            budget         REAL    NOT NULL,
            creator_id     INTEGER NOT NULL,
            created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (creator_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS calorie_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            recipe_id  INTEGER,
            calories   REAL    NOT NULL,
            meal_type  TEXT    NOT NULL,
            date       TEXT    NOT NULL DEFAULT (date('now')),
            FOREIGN KEY (user_id)   REFERENCES users (id),
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        );

        CREATE TABLE IF NOT EXISTS orders (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            recipe_id       INTEGER NOT NULL,
            restaurant_name TEXT    NOT NULL,
            status          TEXT    NOT NULL DEFAULT 'pending',
            created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id)   REFERENCES users (id),
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        );
    """)
    db.commit()


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Database initialized.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)