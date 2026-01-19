from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt

# Inicializamos la aplicación y el sistema de encriptación
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Simulación de base de datos (en memoria por ahora)
users_db = {}

@app.route('/')
def home():
    return "<h1>Sistema de Práctica de Seguridad</h1><p>Usa /register para crear usuario y /login para entrar.</p>"

@app.route('/register', methods=['POST'])
def register():
    """
    Recibe JSON con 'username' y 'password'.
    Guarda la contraseña HASHEADA (no texto plano).
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users_db:
        return jsonify({"msg": "El usuario ya existe"}), 400

    # PASO CRÍTICO DE SEGURIDAD:
    # Generamos el hash de la contraseña. Nunca guardamos la real.
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    users_db[username] = pw_hash
    
    return jsonify({"msg": "Usuario creado exitosamente", "debug_hash": pw_hash}), 201

@app.route('/login', methods=['POST'])
def login():
    """
    Verifica si la contraseña enviada coincide con el hash guardado.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username not in users_db:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    # Verificamos el hash
    stored_hash = users_db[username]
    if bcrypt.check_password_hash(stored_hash, password):
        return jsonify({"msg": "Login Exitoso! Bienvenido al área segura."}), 200
    else:
        return jsonify({"msg": "Contraseña incorrecta"}), 401

if __name__ == '__main__':
    app.run(debug=True)