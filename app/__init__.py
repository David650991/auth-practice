from __future__ import annotations

import os

from dotenv import load_dotenv
from flask import Flask

from app.extensions import bcrypt, db, limiter, login_manager, mail

load_dotenv()


def create_app(config_object=None):
    """Fábrica principal de la aplicación."""

    app = Flask(__name__)

    if config_object is None:
        config_path = os.getenv("FLASK_CONFIG", "config.development.DevelopmentConfig")
        app.config.from_object(config_path)
    else:
        app.config.from_object(config_object)

    _register_extensions(app)
    _register_blueprints(app)

    return app


def _register_extensions(app: Flask) -> None:
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)


def _register_blueprints(app: Flask) -> None:
    from app.blueprints.main import main
    from app.blueprints.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)


__all__ = [
    "create_app",
    "db",
    "bcrypt",
    "login_manager",
    "mail",
    "limiter",
]