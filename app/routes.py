from flask import render_template, url_for, flash, redirect, request
from app import app, bcrypt, users_db

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users_db:
            return render_template('register.html', error="El usuario ya existe")
            
        # Hashing de contraseña (Nivel 1 de seguridad)
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users_db[username] = hashed_password
        
        # Redirigir al login después de registrarse
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Verificación de existencia
        if username not in users_db:
            return render_template('login.html', error="Usuario no encontrado")
            
        # Verificación de hash (Comparación segura)
        stored_hash = users_db[username]
        if bcrypt.check_password_hash(stored_hash, password):
            return f"<h1>¡Bienvenido al sistema seguro, {username}!</h1><p>Acceso concedido.</p>"
        else:
            return render_template('login.html', error="Contraseña incorrecta")
            
    return render_template('login.html')