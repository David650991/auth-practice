from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_user, current_user, login_required
from app import db
from app.models import User
from app.services.biometrics import (
    pipelines,
    repository,
)
from . import auth

# --- VISTAS HTML (Solucion Error 500) ---

@auth.route('/face-enroll-page', methods=['GET'])
@login_required
def face_enroll_page():
    return render_template('face_enroll.html')


@auth.route('/face-login-page', methods=['GET'])
def face_login_page():
    return render_template('face_login.html')


# --- API BIOMETRICA ---

# --- RUTA PARA VALIDACIÓN DE MOVIMIENTOS (Challenge-Response) ---
@auth.route('/check-pose', methods=['POST'])
@login_required
def check_pose():
    """Valida si el usuario está cumpliendo el movimiento solicitado (Sin guardar)."""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'valid': False, 'message': 'Imagen requerida'}), 400

        target_pose = data.get('pose', 'CENTER')
        image_data = data['image']
        
        # Usar pipeline de validación de pose
        is_valid, msg = pipelines.validate_pose_challenge(image_data, target_pose)
        return jsonify({'valid': is_valid, 'message': msg})

    except Exception as e:
        print(f"Error Check Pose: {e}")
        return jsonify({'valid': False, 'message': 'Error IA'}), 500

@auth.route('/face-enroll', methods=['POST'])
@login_required
def face_enroll():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'Sin imagen'}), 400

        image_data = data['image']
        
        # Usar pipeline de enrolamiento
        success, message, encoding = pipelines.enroll_biometric_pipeline(image_data)
        
        if not success:
            return jsonify({'error': message}), 400
        
        # Guardar encoding en la base de datos
        if encoding is not None:
            repository.save_face_encoding(current_user, encoding)
        
        return jsonify({'message': message, 'redirect': '/dashboard'})

    except Exception as e:
        print(f"ERROR ENROLL: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@auth.route('/face-login', methods=['POST'])
def face_login():
    if current_user.is_authenticated:
        return jsonify({'status': 'redirect', 'url': url_for('main.dashboard')})

    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'status': 'error', 'message': 'Sin datos de imagen'}), 400

        image_data = data['image']
        
        # Usar pipeline de login biométrico
        success, message, matching_user = pipelines.login_biometric_pipeline(image_data)
        
        if success and matching_user:
            login_user(matching_user)
            return jsonify({'status': 'success', 'url': url_for('main.dashboard')})
        else:
            return jsonify({'status': 'error', 'message': message}), 401

    except Exception as e:
        print(f"ERROR LOGIN: {e}")
        return jsonify({'status': 'error', 'message': 'Error de sistema'}), 500