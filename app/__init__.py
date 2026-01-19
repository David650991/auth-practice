from flask import Flask
from flask_bcrypt import Bcrypt

# Inicialización del objeto Flask
app = Flask(__name__)

# Configuración de seguridad básica (llave secreta necesaria para sesiones futuras)
app.config['SECRET_KEY'] = 'clave-secreta-temporal-para-desarrollo'

# Inicialización de herramientas de encriptación
bcrypt = Bcrypt(app)

# Base de datos en memoria (Simulada)
# Al estar aquí, es accesible por todo el paquete
users_db = {}

# Importamos las rutas al final para evitar referencias circulares
from app import routes