"""
Configuración centralizada de logging.
Provee loggers pre-configurados por módulo.
"""

import logging
import sys

# Formato consistente para todos los logs
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logging(level=logging.INFO):
    """Configura el logging global de la aplicación."""
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado para el módulo especificado.
    
    Args:
        name: Nombre del módulo (ej: 'biometrics.encoders')
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(f'auth_practice.{name}')
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        logger.addHandler(handler)
    return logger
