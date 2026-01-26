"""Configuración para despliegues productivos."""
from __future__ import annotations

from .base import BaseConfig


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = "production"
    SESSION_COOKIE_SECURE = True
