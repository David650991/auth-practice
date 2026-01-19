from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
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
        
        # Verificar si el usuario ya existe en la Base de Datos
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('register.html', error="El usuario ya existe. Prueba con otro.")
            
        # Encriptar y guardar en la Base de Datos
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit() # ¡Guardado permanente!
        
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Buscar usuario en la DB
        user = User.query.filter_by(username=username).first()
        
        # Verificar contraseña
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user) # Crea la sesión segura
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Usuario o contraseña incorrectos")
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return f"<h1>Panel Seguro</h1><p>Hola, {current_user.username}. Estás logueado permanentemente hasta que salgas.</p><a href='/logout'>Cerrar Sesión</a>"

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))