from __future__ import annotations

import os

from dotenv import load_dotenv
from flask import Flask

from app.extensions import bcrypt, db, limiter, login_manager, mail
from app.logging_config import setup_logging

load_dotenv()


def create_app(config_object=None):
    """Fábrica principal de la aplicación."""
    setup_logging()
    
    app = Flask(__name__)

    if config_object is None:
        config_path = os.getenv("FLASK_CONFIG", "config.development.DevelopmentConfig")
        app.config.from_object(config_path)
    else:
        app.config.from_object(config_object)

    _register_extensions(app)
    _register_jinja_globals(app)
    _register_blueprints(app)
    _ensure_models(app)

    return app


def _register_extensions(app: Flask) -> None:
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)


def _register_jinja_globals(app: Flask) -> None:
    """Registra funciones globales de Jinja."""
    
    def safe_csrf_token():
        """Retorna el CSRF token si está disponible, cadena vacía si no."""
        try:
            from flask_wtf.csrf import generate_csrf
            return generate_csrf()
        except (ImportError, RuntimeError):
            return ''
    
    app.jinja_env.globals['csrf_token'] = safe_csrf_token


def _register_blueprints(app: Flask) -> None:
    from app.blueprints.main import main
    from app.blueprints.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)


def _ensure_models(app: Flask) -> None:
    """Verifica y descarga modelos ML al iniciar (solo si no es testing)."""
    if app.config.get('TESTING'):
        return
    
    from app.models_manager import ensure_all_models
    ensure_all_models()


__all__ = [
    "create_app",
    "db",
    "bcrypt",
    "login_manager",
    "mail",
    "limiter",
]