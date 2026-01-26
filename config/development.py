"""Configuración para desarrollo local."""
from __future__ import annotations

from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = "development"
    TESTING = False
