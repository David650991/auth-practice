"""
Gestor de modelos ML para la aplicación.
Verifica y descarga modelos necesarios al iniciar.
"""

import urllib.request
import bz2
import os
from pathlib import Path

from app.logging_config import get_logger

logger = get_logger('models.manager')

# Configuración de modelos
MODELS_DIR = Path(__file__).parent / 'static' / 'models'
DLIB_MODEL = {
    'filename': 'shape_predictor_68_face_landmarks.dat',
    'url': 'http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2',
    'size_mb': 95
}


def ensure_models_directory():
    """Crea el directorio de modelos si no existe."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Directorio de modelos: {MODELS_DIR}")


def is_model_present(filename: str) -> bool:
    """Verifica si un modelo ya está descargado."""
    return (MODELS_DIR / filename).exists()


def download_dlib_model() -> bool:
    """
    Descarga y descomprime el modelo de landmarks de Dlib.
    
    Returns:
        bool: True si el modelo está listo, False si hubo error
    """
    model_path = MODELS_DIR / DLIB_MODEL['filename']
    
    if model_path.exists():
        logger.info(f"Modelo Dlib ya presente: {model_path}")
        return True
    
    ensure_models_directory()
    
    logger.info(f"Descargando modelo Dlib ({DLIB_MODEL['size_mb']} MB)...")
    logger.info("Esto puede tardar unos minutos según tu conexión.")
    
    bz2_path = model_path.with_suffix('.dat.bz2')
    
    try:
        urllib.request.urlretrieve(DLIB_MODEL['url'], bz2_path)
        logger.info("Descarga completada. Descomprimiendo...")
        
        with bz2.BZ2File(bz2_path) as fr, open(model_path, 'wb') as fw:
            fw.write(fr.read())
        
        bz2_path.unlink()  # Eliminar archivo comprimido
        logger.info(f"Modelo instalado: {model_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error descargando modelo Dlib: {e}", exc_info=True)
        return False


def ensure_all_models() -> bool:
    """
    Verifica y descarga todos los modelos necesarios.
    Llamar al iniciar la aplicación.
    
    Returns:
        bool: True si todos los modelos están listos
    """
    logger.info("Verificando modelos ML...")
    
    dlib_ok = download_dlib_model()
    
    if dlib_ok:
        logger.info("Todos los modelos están listos")
    else:
        logger.warning("Algunos modelos no pudieron descargarse")
    
    return dlib_ok
