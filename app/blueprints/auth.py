from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app import db, bcrypt, limiter # Importamos el limiter aquí
from app.models import User
from flask_login import login_user, logout_user, login_required, current_user
import pyotp
import qrcode
import io
import base64
import re # Necesario para las expresiones regulares

auth = Blueprint('auth', __name__)

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # --- AUDITORÍA DE SEGURIDAD: VALIDACIÓN DE CONTRASEÑA ---
        # 1. Longitud mínima de 8 caracteres
        if len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'danger')
            return redirect(url_for('auth.register'))
            
        # 2. Debe contener al menos una mayúscula, un número y un carácter especial
        if not re.search(r"[A-Z]", password):
            flash('La contraseña debe incluir al menos una letra mayúscula.', 'danger')
            return redirect(url_for('auth.register'))
            
        if not re.search(r"\d", password):
            flash('La contraseña debe incluir al menos un número.', 'danger')
            return redirect(url_for('auth.register'))

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            flash('La contraseña debe incluir al menos un carácter especial (!@#$...).', 'danger')
            return redirect(url_for('auth.register'))
        # ---------------------------------------------------------

        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe.', 'danger')
            return redirect(url_for('auth.register'))
            
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        
        flash('Cuenta creada. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth.route("/login", methods=['GET', 'POST'])
@limiter.limit("5 per minute") # --- AUDITORÍA: DEFENSA ACTIVA CONTRA FUERZA BRUTA ---
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            # Si el usuario tiene 2FA activado, redirigir a verificación
            if user.otp_secret:
                session['2fa_user_id'] = user.id 
                return redirect(url_for('auth.verify_2fa_login'))
            
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Inicio de sesión fallido. Verifica usuario y contraseña.', 'danger')
            
    return render_template('login.html')

@auth.route("/verify-2fa-login", methods=['GET', 'POST'])
@limiter.limit("5 per minute") # Protegemos también la validación del token
def verify_2fa_login():
    if '2fa_user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        token = request.form.get('token')
        user = User.query.get(session['2fa_user_id'])
        
        if user and user.otp_secret:
            totp = pyotp.TOTP(user.otp_secret)
            # Verificamos Token de App O Códigos de Respaldo
            is_valid_token = totp.verify(token)
            is_valid_backup = False

            if not is_valid_token and user.backup_codes:
                codes = user.backup_codes.split(",")
                if token in codes:
                    is_valid_backup = True
                    codes.remove(token) # Quemamos el código usado
                    user.backup_codes = ",".join(codes)
                    db.session.commit()

            if is_valid_token or is_valid_backup:
                login_user(user)
                session.pop('2fa_user_id', None)
                return redirect(url_for('main.dashboard'))
            else:
                flash('Código inválido.', 'danger')
                
    return render_template('verify_2fa.html')

@auth.route("/enable-2fa")
@login_required
def enable_2fa():
    if not current_user.otp_secret:
        secret = pyotp.random_base32()
        current_user.otp_secret = secret
        # Generamos códigos de backup al activar
        import secrets
        backup_codes = [secrets.token_hex(4) for _ in range(5)]
        current_user.backup_codes = ",".join(backup_codes)
        db.session.commit()
    
    totp = pyotp.TOTP(current_user.otp_secret)
    uri = totp.provisioning_uri(name=current_user.username, issuer_name="AuthPractice")
    
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return render_template('enable_2fa.html', qr_code=img_b64, secret=current_user.otp_secret, backup_codes=current_user.backup_codes.split(","))

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))