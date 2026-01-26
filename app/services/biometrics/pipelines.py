"""
Módulo de orquestación de flujos biométricos (Pipelines).
Responsabilidades:
  - Orquestar el flujo de enrolamiento (captura, validación, almacenamiento)
  - Orquestar el flujo de login (captura, reconocimiento, autenticación)
  - Orquestar flujos de desafío de pose (liveness challenge-response)
"""

import cv2
from app.services.biometrics import encoders, pose_checks, repository


def enroll_biometric_pipeline(image_data):
    """
    Orquesta el proceso completo de enrolamiento biométrico.
    Pasos:
      1. Decodificar imagen Base64
      2. Detectar rostros
      3. Validar estructura facial (anti-spoofing, liveness)
      4. Generar encoding facial
    
    Args:
        image_data (str): Datos de imagen Base64
    
    Returns:
        tuple: (éxito: bool, mensaje: str, encoding: ndarray o None)
    """
    # Paso 1: Decodificar imagen
    img_bgr, img_gray = encoders.decode_base64_image(image_data)
    if img_bgr is None:
        return False, "Imagen corrupta", None
    
    # Paso 2: Detectar rostros
    height, width = img_gray.shape
    boxes = encoders.detect_faces(img_gray, model="hog")
    
    if not boxes:
        return False, "Rostro no detectado.", None
    if len(boxes) > 1:
        return False, "Multiples rostros detectados.", None
    
    # Paso 3: Validar estructura facial
    is_valid, validation_msg = pose_checks.analyze_face_structure(
        img_gray, boxes[0], width, height
    )
    if not is_valid:
        return False, f"Rechazado: {validation_msg}", None
    
    # Paso 4: Generar encoding
    img_rgb = encoders.prepare_image_for_encoding(img_bgr)
    if img_rgb is None:
        return False, "No se pudo procesar la imagen", None
    
    encodings = encoders.extract_face_encodings(img_bgr, boxes)
    if not encodings:
        return False, "No se pudo generar huella.", None
    
    return True, "Registro Biométrico Exitoso", encodings[0]


def login_biometric_pipeline(image_data, tolerance=0.45):
    """
    Orquesta el proceso completo de login biométrico.
    Pasos:
      1. Decodificar imagen Base64
      2. Detectar rostros
      3. Validar estructura facial (anti-spoofing, liveness)
      4. Generar encoding facial
      5. Comparar con encodings almacenados en BD
    
    Args:
        image_data (str): Datos de imagen Base64
        tolerance (float): Umbral para comparación de rostros (0.0-1.0)
    
    Returns:
        tuple: (éxito: bool, mensaje: str, usuario: User o None)
    """
    # Paso 1: Decodificar imagen
    img_bgr, img_gray = encoders.decode_base64_image(image_data)
    if img_bgr is None:
        return False, "Sin datos de imagen", None
    
    # Paso 2: Detectar rostros
    boxes = encoders.detect_faces(img_gray, model="hog")
    if not boxes:
        return False, "Rostro no visible", None
    
    height, width = img_gray.shape
    
    # Paso 3: Validar estructura facial
    is_valid, validation_msg = pose_checks.analyze_face_structure(
        img_gray, boxes[0], width, height
    )
    if not is_valid:
        return False, f"Seguridad: {validation_msg}", None
    
    # Paso 4: Generar encoding
    img_rgb = encoders.prepare_image_for_encoding(img_bgr)
    if img_rgb is None:
        return False, "Error procesando imagen", None
    
    encodings = encoders.extract_face_encodings(img_bgr, boxes)
    if not encodings:
        return False, "Error extrayendo características", None
    
    unknown_enc = encodings[0]
    
    # Paso 5: Comparar con usuarios registrados
    matching_user = repository.find_matching_user(unknown_enc, tolerance=tolerance)
    
    if matching_user:
        return True, "Acceso Permitido", matching_user
    else:
        return False, "Acceso Denegado", None


def validate_pose_challenge(image_data, target_pose):
    """
    Orquesta un desafío de pose (challenge-response liveness).
    Pasos:
      1. Decodificar imagen Base64
      2. Detectar rostros
      3. Validar que el rostro cumple la pose requerida
    
    Args:
        image_data (str): Datos de imagen Base64
        target_pose (str): Pose requerida ('CENTER', 'LEFT', 'RIGHT', 'UP', 'DOWN')
    
    Returns:
        tuple: (válido: bool, mensaje: str)
    """
    # Paso 1: Decodificar imagen
    img_bgr, img_gray = encoders.decode_base64_image(image_data)
    if img_bgr is None:
        return False, "Imagen inválida"
    
    # Paso 2: Detectar rostros
    height, width = img_gray.shape
    boxes = encoders.detect_faces(img_gray, model="hog")
    
    if not boxes:
        return False, "Rostro no encontrado"
    
    # Paso 3: Validar pose
    is_valid, msg = pose_checks.validate_pose(
        img_gray, boxes[0], width, target_pose
    )
    
    return is_valid, msg
