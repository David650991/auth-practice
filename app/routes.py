import re  # <--- NUEVA IMPORTACIÓN PARA VALIDAR TEXTO
from flask import render_template, url_for, flash, redirect, request
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
        
        # --- NUEVA CAPA DE SEGURIDAD: VALIDACIÓN DE CONTRASEÑA ---
        if len(password) < 8:
            return render_template('register.html', error="La contraseña es muy corta (mínimo 8 caracteres).")
        if not re.search(r"\d", password):
            return render_template('register.html', error="La contraseña debe incluir al menos un número.")
        if not re.search(r"[A-Z]", password):
            return render_template('register.html', error="La contraseña debe incluir al menos una mayúscula.")
        # ---------------------------------------------------------

        # Verificar si el usuario ya existe
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('register.html', error="El usuario ya existe. Prueba con otro.")
            
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
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return f"<h1>Panel Seguro</h1><p>Hola, {current_user.username}. Tu cuenta cumple con los estándares de seguridad.</p><a href='/logout'>Cerrar Sesión</a>"

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))