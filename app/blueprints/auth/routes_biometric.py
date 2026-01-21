from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, current_user, login_required
from app import db
from app.models import User
from . import auth 
import face_recognition
import numpy as np
import base64
import cv2
import sys
import pickle

def base64_to_image(base64_string):
    """Decodifica, valida y estandariza la imagen para Dlib."""
    try:
        # 1. Limpieza
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # 2. Bytes
        img_bytes = base64.b64decode(base64_string)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        
        # 3. Decodificar OpenCV
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # 4. Validaciones de integridad
        if img is None or img.size == 0:
            print("Error: Imagen vacía o corrupta.", file=sys.stderr)
            return None
            
        return img
    except Exception as e:
        print(f"Error en base64_to_image: {e}", file=sys.stderr)
        return None

def prepare_for_dlib(img_bgr):
    """
    Convierte la imagen BGR de OpenCV a RGB y asegura 
    compatibilidad de memoria para Dlib/FaceRecognition.
    """
    try:
        # 1. Convertir color
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        
        # 2. PARCHE CRÍTICO: Forzar array contiguo y tipo uint8
        # Esto soluciona el error "Unsupported image type"
        img_rgb = np.ascontiguousarray(img_rgb, dtype=np.uint8)
        
        return img_rgb
    except Exception as e:
        print(f"Error preparando imagen para Dlib: {e}", file=sys.stderr)
        return None

# --- RUTAS ---

@auth.route('/face-enroll', methods=['POST'])
@login_required
def face_enroll():
    """
    Recibe una imagen en Base64 desde la webcam, detecta el rostro
    usando estrategia híbrida (Gris/RGB) para compatibilidad con Numpy 2.x
    """
    try:
        data = request.get_json()
        image_data = data.get('image')

        if not image_data:
            return jsonify({'error': 'No se recibió ninguna imagen'}), 400

        # --- 1. DECODIFICACIÓN ---
        if ',' in image_data:
            encoded_data = image_data.split(',')[1]
        else:
            encoded_data = image_data

        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Fallo al decodificar la imagen'}), 400

        print(f"DEBUG: Imagen recibida. Shape: {img.shape}, Dtype: {img.dtype}")

        # --- 2. DETECCIÓN (ESTRATEGIA BLINDADA) ---
        # Convertimos a Escala de Grises para la detección. 
        # Esto elimina problemas de canales de color en Dlib.
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # IMPORTANTE: Hacemos una copia explícita para limpiar la memoria
        gray_clean = np.array(gray, copy=True)
        
        print("DEBUG: Iniciando detección de rostro en Grayscale...")
        boxes = face_recognition.face_locations(gray_clean, model="hog")

        if not boxes:
            print("DEBUG: Rostro no encontrado.")
            return jsonify({'error': 'No se detectó ningún rostro. Ajusta la iluminación.'}), 400
        
        if len(boxes) > 1:
            return jsonify({'error': 'Múltiples rostros detectados. Quédate solo en la cámara.'}), 400

        # --- 3. ENCODING (EXTRACCIÓN DE DATOS) ---
        # Dlib necesita RGB para el encoding detallado.
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # IMPORTANTE: Copia profunda del RGB. 
        # 'order=C' fuerza el orden de memoria C que exige Dlib.
        rgb_clean = np.array(rgb, copy=True, order='C')

        print("DEBUG: Iniciando encoding facial en RGB...")
        # Pasamos los boxes ya encontrados en gris, aplicados a la imagen color
        encodings = face_recognition.face_encodings(rgb_clean, boxes)
        
        if not encodings:
            return jsonify({'error': 'Error al generar huella facial. Intenta de nuevo.'}), 400

        face_encoding = encodings[0]

        # --- 4. GUARDADO ---
        current_user.face_encoding = pickle.dumps(face_encoding)
        db.session.commit()
        
        print(f"DEBUG: Éxito. Usuario {current_user.username} enrolado.")
        return jsonify({'message': 'Biometría registrada exitosamente', 'redirect': '/dashboard'})

    except Exception as e:
        # Imprimimos el error completo en la terminal para diagnóstico
        print(f"ERROR CRÍTICO EN FACE ENROLL: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@auth.route('/face-login', methods=['POST'])
def face_login():
    if current_user.is_authenticated:
        return jsonify({'status': 'redirect', 'url': url_for('main.dashboard')})

    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({'status': 'error', 'message': 'Sin datos de imagen'}), 400

    try:
        img = base64_to_image(image_data)
        if img is None:
            return jsonify({'status': 'error', 'message': 'Imagen ilegible'}), 400

        # Parche de compatibilidad también aquí
        rgb_img = prepare_for_dlib(img)
        
        face_locations = face_recognition.face_locations(rgb_img, model="hog")
        if not face_locations:
            return jsonify({'status': 'error', 'message': 'No veo tu rostro.'}), 400
            
        unknown_encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]

        users = User.query.filter(User.face_encoding.isnot(None)).all()
        found_user = None
        
        # Comparación
        for user in users:
            known_encoding = user.get_face_encoding()
            if known_encoding is not None:
                matches = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.5)
                if matches[0]:
                    found_user = user
                    break
        
        if found_user:
            login_user(found_user)
            return jsonify({'status': 'success', 'url': url_for('main.dashboard')})
        else:
            return jsonify({'status': 'error', 'message': 'Rostro no registrado.'}), 401

    except Exception as e:
        print(f"EXCEPCION LOGIN: {e}", file=sys.stderr)
        return jsonify({'status': 'error', 'message': 'Error de sistema.'}), 500

# VISTAS
@auth.route('/face-enroll-page')
@login_required
def face_enroll_page():
    return render_template('face_enroll.html')

@auth.route('/face-login-page')
def face_login_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('face_login.html')