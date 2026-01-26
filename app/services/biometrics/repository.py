"""
Módulo de repositorio biométrico (CRUD de face encodings).
Responsabilidades:
  - Almacenamiento y recuperación de encodings faciales
  - Persistencia en base de datos vía SQLAlchemy
  - Comparación de rostros usando face_recognition
"""

import pickle
import face_recognition
from app import db
from app.models import User
from app.logging_config import get_logger

logger = get_logger('biometrics.repository')


def save_face_encoding(user, encoding):
    """
    Guarda el encoding facial de un usuario en la base de datos.
    
    Args:
        user (User): Objeto de usuario
        encoding (ndarray): Array NumPy con el vector de características (128D)
    
    Returns:
        bool: True si se guardó exitosamente, False si hubo error
    """
    try:
        user.face_encoding = pickle.dumps(encoding)
        db.session.commit()
        logger.info(f"Encoding guardado para usuario {user.id}")
        return True
    except Exception as e:
        logger.error(f"Error guardando encoding para usuario {user.id}: {e}", exc_info=True)
        db.session.rollback()
        return False


def load_face_encoding(user):
    """
    Carga el encoding facial de un usuario desde la base de datos.
    
    Args:
        user (User): Objeto de usuario
    
    Returns:
        ndarray: Array NumPy con el vector de características, o None si no existe
    """
    try:
        if not user.face_encoding:
            return None
        encoding = pickle.loads(user.face_encoding)
        return encoding
    except Exception as e:
        logger.error(f"Error cargando encoding para usuario {user.id}: {e}", exc_info=True)
        return None


def get_all_face_encodings():
    """
    Obtiene todos los usuarios con encodings guardados.
    
    Returns:
        list: Lista de objetos User que tienen face_encoding registrado
    """
    try:
        users = User.query.filter(User.face_encoding.isnot(None)).all()
        logger.debug(f"Usuarios con encoding: {len(users)}")
        return users
    except Exception as e:
        logger.error(f"Error obteniendo encodings: {e}", exc_info=True)
        return []


def compare_faces(known_encoding, unknown_encoding, tolerance=0.45):
    """
    Compara dos encodings faciales y determina si corresponden al mismo rostro.
    
    Args:
        known_encoding (ndarray): Encoding conocido (de base de datos)
        unknown_encoding (ndarray): Encoding desconocido (capturado en tiempo real)
        tolerance (float): Umbral de tolerancia (0.0-1.0). Valores más bajos = más estricto.
    
    Returns:
        bool: True si los rostros coinciden, False en caso contrario
    """
    try:
        matches = face_recognition.compare_faces(
            [known_encoding],
            unknown_encoding,
            tolerance=tolerance
        )
        return matches[0] if matches else False
    except Exception as e:
        logger.error(f"Error comparando encodings: {e}", exc_info=True)
        return False


def find_matching_user(unknown_encoding, tolerance=0.45):
    """
    Busca un usuario que coincida con el encoding desconocido.
    
    Args:
        unknown_encoding (ndarray): Encoding facial capturado
        tolerance (float): Umbral de tolerancia para comparación
    
    Returns:
        User: Objeto User si se encuentra coincidencia, None en caso contrario
    """
    try:
        users = get_all_face_encodings()
        
        for user in users:
            known_encoding = load_face_encoding(user)
            if known_encoding is None:
                continue
            
            if compare_faces(known_encoding, unknown_encoding, tolerance):
                logger.info(f"Match encontrado: usuario {user.id}")
                return user
        
        logger.debug("No se encontró match")
        return None
    except Exception as e:
        logger.error(f"Error buscando usuario coincidente: {e}", exc_info=True)
        return None


def clear_face_encoding(user):
    """
    Elimina el encoding facial de un usuario.
    
    Args:
        user (User): Objeto de usuario
    
    Returns:
        bool: True si se eliminó exitosamente, False si hubo error
    """
    try:
        user.face_encoding = None
        db.session.commit()
        logger.info(f"Encoding eliminado para usuario {user.id}")
        return True
    except Exception as e:
        logger.error(f"Error eliminando encoding para usuario {user.id}: {e}", exc_info=True)
        db.session.rollback()
        return False
