from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user
from app import db, bcrypt, limiter
from app.models import User
from .utils import send_confirmation_email
from . import auth 
import re
from datetime import datetime

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email').lower()
        phone = request.form.get('phone') # <--- NUEVO
        password = request.form.get('password')
        
        # Validaciones
        if len(password) < 8 or not re.search(r"[A-Z]", password) or \
           not re.search(r"\d", password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            flash('La contraseña no cumple los requisitos de seguridad.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe.', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Ese correo ya está registrado.', 'danger')
            return redirect(url_for('auth.register'))

        # Validación básica de teléfono (opcional, se puede mejorar con Regex)
        if User.query.filter_by(phone_number=phone).first():
            flash('Ese número de teléfono ya está registrado.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Guardamos teléfono
        user = User(username=username, email=email, phone_number=phone, password=hashed_pw, confirmed=False)
        db.session.add(user)
        db.session.commit()
        
        send_confirmation_email(user)
        flash('Cuenta creada. ¡Revisa tu correo para activar tu cuenta!', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth.route("/confirm/<token>")
def confirm_email(token):
    try:
        user = User.verify_token(token, salt='email-confirm-salt')
    except:
        flash('El enlace de confirmación es inválido o ha expirado.', 'danger')
        return redirect(url_for('auth.login'))
        
    if user and not user.confirmed:
        user.confirmed = True
        user.confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('¡Cuenta confirmada exitosamente! Ahora puedes iniciar sesión.', 'success')
    elif user and user.confirmed:
        flash('Tu cuenta ya estaba confirmada.', 'info')
        
    return redirect(url_for('auth.login'))

@auth.route("/login", methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            if not user.confirmed:
                flash('Debes confirmar tu correo electrónico antes de entrar.', 'warning')
                return render_template('login.html')

            if user.otp_secret:
                session['2fa_user_id'] = user.id 
                return redirect(url_for('auth.verify_2fa_login'))
            
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Credenciales incorrectas.', 'danger')
            
    return render_template('login.html')

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))