"""
Módulo de codificación facial (Extractores de características biométricas).
Responsabilidades:
  - Decodificación de imágenes Base64
  - Detección de rostros usando face_recognition
  - Generación de vectores de características faciales (face encodings)
"""

import base64
import cv2
import numpy as np
import face_recognition


def decode_base64_image(image_data):
    """
    Decodifica una imagen Base64 a formato OpenCV.
    
    Args:
        image_data (str): Datos de imagen en Base64 (con o sin prefijo 'data:image/jpeg;base64,')
    
    Returns:
        tuple: (imagen_BGR, imagen_gris) o (None, None) si hay error
    """
    try:
        # Remover prefijo data URI si existe
        if ',' in image_data:
            encoded = image_data.split(',')[1]
        else:
            encoded = image_data
        
        # Decodificar Base64
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img_bgr is None:
            return None, None
        
        # Convertir a escala de grises
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        return img_bgr, img_gray
    
    except Exception as e:
        print(f"Error decodificando imagen: {e}")
        return None, None


def detect_faces(image_gray, model="hog"):
    """
    Detecta rostros en una imagen usando face_recognition.
    
    Args:
        image_gray (ndarray): Imagen en escala de grises
        model (str): Modelo de detección ('hog' o 'cnn'). HOG es rápido, CNN es más preciso.
    
    Returns:
        list: Lista de rectanglos (top, right, bottom, left) de rostros detectados
    """
    try:
        boxes = face_recognition.face_locations(image_gray, model=model)
        return boxes
    except Exception as e:
        print(f"Error detectando rostros: {e}")
        return []


def extract_face_encodings(image_bgr, face_boxes):
    """
    Extrae vectores de características faciales (embeddings) de los rostros detectados.
    
    Args:
        image_bgr (ndarray): Imagen en formato BGR (color)
        face_boxes (list): Lista de rectángulos (top, right, bottom, left)
    
    Returns:
        list: Lista de arrays NumPy con las características faciales (128D vectors)
    """
    try:
        # Convertir BGR a RGB (face_recognition requiere RGB)
        img_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        
        # Asegurar que el array es continuo en memoria (C-contiguous)
        img_rgb = np.array(img_rgb, copy=True, order='C')
        
        # Generar encodings
        encodings = face_recognition.face_encodings(img_rgb, face_boxes)
        return encodings
    
    except Exception as e:
        print(f"Error extrayendo encodings: {e}")
        return []


def prepare_image_for_encoding(image_bgr):
    """
    Prepara la imagen BGR para generación de encodings.
    Convierte BGR→RGB y asegura formato C-contiguous.
    
    Args:
        image_bgr (ndarray): Imagen en formato BGR
    
    Returns:
        ndarray: Imagen RGB lista para face_recognition
    """
    try:
        img_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        img_rgb = np.array(img_rgb, copy=True, order='C')
        return img_rgb
    except Exception as e:
        print(f"Error preparando imagen: {e}")
        return None
