import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Cargamos las variables del archivo .env
load_dotenv()

app = Flask(__name__)

# Configuración de Seguridad usando Variables de Entorno
# Si no encuentra la clave en .env, usará la segunda opción por defecto (solo para evitar crasheos)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')

# Inicialización de Extensiones
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Inicialización del Escudo (Limiter)
limiter = Limiter(
    get_remote_address, 
    app=app, 
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

from app import routes
from app import models