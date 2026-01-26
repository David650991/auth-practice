"""
Módulo de validación de pose facial y análisis de estructura biométrica.
Responsabilidades:
  - Extracción de métricas faciales (yaw, pitch, proximidad)
  - Validación de desafíos de pose (CENTER, LEFT, RIGHT, UP, DOWN)
  - Análisis de liveness (detección de ojos abiertos)
  - Validación de estructura facial para anti-spoofing
"""

import cv2
import numpy as np
import dlib
import os
from scipy.spatial import distance as dist

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, 'static', 'models', 'shape_predictor_68_face_landmarks.dat')

predictor = None
try:
    if os.path.exists(MODEL_PATH):
        predictor = dlib.shape_predictor(MODEL_PATH)
    else:
        print("CRITICAL: Modelo de landmarks no encontrado.")
except Exception as e:
    print(f"CRITICAL: Error cargando Dlib: {e}")

# Puntos clave
NOSE_TIP = 30
LEFT_EYE = 36  # Ojo derecho en espejo
RIGHT_EYE = 45  # Ojo izquierdo en espejo
MOUTH_TOP = 51
(lStart, lEnd) = (42, 48)
(rStart, rEnd) = (36, 42)


def get_face_metrics(gray, rect):
    """Extrae métricas geométricas clave para determinar pose."""
    if predictor is None:
        return None

    dlib_rect = dlib.rectangle(int(rect[3]), int(rect[0]), int(rect[1]), int(rect[2]))
    shape = predictor(gray, dlib_rect)
    coords = np.zeros((68, 2), dtype="int")
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)

    # 1. Yaw (Lados)
    nose_x = coords[NOSE_TIP][0]
    left_eye_x = coords[LEFT_EYE][0]
    right_eye_x = coords[RIGHT_EYE][0]
    d_left = nose_x - left_eye_x
    d_right = right_eye_x - nose_x
    if d_right == 0:
        d_right = 0.001
    yaw_ratio = d_left / d_right  # < 0.6 Derecha, > 1.6 Izquierda

    # 2. Pitch (Vertical)
    eyes_y = (coords[LEFT_EYE][1] + coords[RIGHT_EYE][1]) / 2
    nose_y = coords[NOSE_TIP][1]
    mouth_y = coords[MOUTH_TOP][1]
    d_up = nose_y - eyes_y
    d_down = mouth_y - nose_y
    if d_down == 0:
        d_down = 0.001
    pitch_ratio = d_up / d_down  # < 0.5 Arriba, > 1.8 Abajo

    # 3. Proximidad
    face_width = dist.euclidean((coords[0][0], coords[0][1]), (coords[16][0], coords[16][1]))

    return {
        "yaw": yaw_ratio,
        "pitch": pitch_ratio,
        "width": face_width,
        "coords": coords,
    }


def validate_pose(gray, rect, img_width, target_pose):
    """
    Verifica si el rostro cumple con la pose solicitada por la IA.
    Target Poses: 'CENTER', 'LEFT', 'RIGHT', 'UP', 'DOWN'
    """
    metrics = get_face_metrics(gray, rect)
    if not metrics:
        return False, "Error IA"

    yaw = metrics["yaw"]
    pitch = metrics["pitch"]
    proximity = metrics["width"] / img_width

    # Validación de Proximidad base (para cualquier pose)
    if proximity < 0.22:
        return False, "ACÉRCATE MÁS"

    if target_pose == 'CENTER':
        if yaw < 0.7:
            return False, "MIRA AL CENTRO (Vas derecha)"
        if yaw > 1.4:
            return False, "MIRA AL CENTRO (Vas izquierda)"
        if pitch < 0.55:
            return False, "BAJA LA CABEZA"
        if pitch > 1.5:
            return False, "SUBE LA CABEZA"
        return True, "Posición Correcta"

    if target_pose == 'LEFT':  # Usuario gira su cara a la izquierda (nuestra derecha visual)
        if yaw < 0.6:
            return True, "Giro Detectado"
        return False, "GIRA A TU IZQUIERDA"

    if target_pose == 'RIGHT':
        if yaw > 1.5:
            return True, "Giro Detectado"
        return False, "GIRA A TU DERECHA"

    if target_pose == 'UP':
        if pitch < 0.5:
            return True, "Movimiento Detectado"
        return False, "MIRA HACIA ARRIBA"

    if target_pose == 'DOWN':
        if pitch > 1.7:
            return True, "Movimiento Detectado"
        return False, "MIRA HACIA ABAJO"

    return False, "Pose desconocida"


def eye_aspect_ratio(eye):
    """Calcula si el ojo está abierto (EAR)"""
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)


def analyze_face_structure(gray_image, rect, img_width, img_height):
    """
    Retorna: (EsValido, Mensaje)
    Valida: Liveness (Ojos), Proximidad, Yaw y Pitch (pose neutra).
    """
    if predictor is None:
        return True, "Modo Dev (Sin Modelo)"

    try:
        metrics = get_face_metrics(gray_image, rect)
        if not metrics:
            return False, "Error de análisis biométrico."

        coords = metrics["coords"]

        # --- Liveness (ojos) ---
        leftEye = coords[lStart:lEnd]
        rightEye = coords[rStart:rEnd]
        avgEAR = (eye_aspect_ratio(leftEye) + eye_aspect_ratio(rightEye)) / 2.0
        if avgEAR < 0.18:
            return False, "OJOS CERRADOS. Ábrelos bien."

        # --- Proximidad ---
        proximity = metrics["width"] / img_width
        if proximity < 0.28:
            return False, "DEMASIADO LEJOS. Acércate más a la cámara."

        # --- Orientaciones ---
        yaw_ratio = metrics["yaw"]
        if yaw_ratio < 0.7:
            return False, "GIRA AL CENTRO (Miras a derecha)."
        if yaw_ratio > 1.4:
            return False, "GIRA AL CENTRO (Miras a izquierda)."

        pitch_ratio = metrics["pitch"]
        if pitch_ratio < 0.5:
            return False, "BAJA LA CABEZA (Miras arriba)."
        if pitch_ratio > 1.8:
            return False, "SUBE LA CABEZA (Miras abajo)."

        return True, "Calidad Biométrica Aceptada"

    except Exception as e:
        print(f"Error lógica bio: {e}")
        return False, "Error de análisis biométrico."
