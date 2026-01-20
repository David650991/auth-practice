from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, login_required, current_user
from app import db, bcrypt, limiter
from app.models import User
from .utils import send_reset_email
from . import auth # Importamos el Blueprint compartido
import pyotp, qrcode, io, base64, secrets, re

@auth.route("/verify-2fa-login", methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def verify_2fa_login():
    if '2fa_user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        token = request.form.get('token')
        user = User.query.get(session['2fa_user_id'])
        
        if user and user.otp_secret:
            totp = pyotp.TOTP(user.otp_secret)
            is_valid_token = totp.verify(token)
            is_valid_backup = False

            if not is_valid_token and user.backup_codes:
                codes = user.backup_codes.split(",")
                if token in codes:
                    is_valid_backup = True
                    codes.remove(token)
                    user.backup_codes = ",".join(codes)
                    db.session.commit()

            if is_valid_token or is_valid_backup:
                login_user(user)
                session.pop('2fa_user_id', None)
                return redirect(url_for('main.dashboard'))
            else:
                flash('Código inválido.', 'danger')
    return render_template('verify_2fa.html')

@auth.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email').lower()
        user = User.query.filter_by(email=email).first()
        if user:
            send_reset_email(user)
        flash('Si el correo existe, recibirás instrucciones.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('reset_request.html')

@auth.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    user = User.verify_token(token, salt='password-reset-salt')
    if user is None:
        flash('Token inválido o expirado.', 'warning')
        return redirect(url_for('auth.reset_request'))
        
    if request.method == 'POST':
        password = request.form.get('password')
        if len(password) < 8 or not re.search(r"[A-Z]", password) or \
           not re.search(r"\d", password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            flash('La contraseña es débil.', 'danger')
            return redirect(url_for('auth.reset_token', token=token))
            
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash('Contraseña actualizada. Inicia sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_token.html')

@auth.route("/enable-2fa")
@login_required
def enable_2fa():
    if not current_user.otp_secret:
        secret = pyotp.random_base32()
        current_user.otp_secret = secret
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