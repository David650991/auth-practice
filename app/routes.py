import re
import pyotp
import qrcode
import io
from base64 import b64encode
from flask import render_template, url_for, flash, redirect, request, session
from app import app, db, bcrypt, limiter
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validaciones
        if len(password) < 8:
            return render_template('register.html', error="La contraseña es muy corta (mínimo 8 caracteres).")
        if not re.search(r"\d", password):
            return render_template('register.html', error="La contraseña debe incluir al menos un número.")
        if not re.search(r"[A-Z]", password):
            return render_template('register.html', error="La contraseña debe incluir al menos una mayúscula.")

        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('register.html', error="El usuario ya existe.")
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute") 
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            # --- LÓGICA DE 2FA ---
            if user.otp_secret:
                # Si tiene 2FA, NO lo logueamos todavía.
                # Guardamos quién dice ser en una sesión temporal insegura
                session['2fa_user_id'] = user.id
                return redirect(url_for('verify_2fa'))
            else:
                # Si NO tiene 2FA, entra directo (Nivel bajo de seguridad)
                login_user(user)
                return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
            
    return render_template('login.html')

# --- NUEVA RUTA: VERIFICACIÓN DEL CÓDIGO ---
@app.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    # Si no hay un usuario esperando en el limbo, adiós
    if '2fa_user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_id = session['2fa_user_id']
        user = User.query.get(user_id)
        token = request.form.get('token')
        
        # Matemáticas de verificación (TOTP)
        totp = pyotp.TOTP(user.otp_secret)
        if totp.verify(token):
            # ¡CÓDIGO CORRECTO! Ahora sí le damos acceso real
            login_user(user)
            session.pop('2fa_user_id', None) # Limpiamos la sesión temporal
            return redirect(url_for('dashboard'))
        else:
            return render_template('verify_2fa.html', error="Código inválido o expirado")
            
    return render_template('verify_2fa.html')

@app.route('/dashboard')
@login_required
def dashboard():
    estado_2fa = "ACTIVADO" if current_user.otp_secret else "DESACTIVADO"
    return render_template('dashboard.html', usuario=current_user.username, estado_2fa=estado_2fa)

@app.route('/logout')
def logout():
    logout_user()
    session.pop('2fa_user_id', None) # Limpieza por seguridad
    return redirect(url_for('home'))

@app.route('/enable-2fa')
@login_required
def enable_2fa():
    if not current_user.otp_secret:
        secret = pyotp.random_base32()
        current_user.otp_secret = secret
        db.session.commit()
    else:
        secret = current_user.otp_secret

    otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.username, 
        issuer_name="Auth-Practice-App"
    )

    img = qrcode.make(otp_uri)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    qr_b64 = b64encode(buf.getvalue()).decode('ascii')

    return render_template('enable_2fa.html', qr_code=qr_b64, secret=secret)