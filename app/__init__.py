from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

# Configuración de Seguridad
app.config['SECRET_KEY'] = 'clave-secreta-temporal-para-desarrollo'
# Configuración de la Base de Datos (se creará un archivo site.db local)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Inicialización de Extensiones
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Si alguien intenta entrar a zona segura sin permiso, lo manda aquí

# Importamos rutas y modelos al final para evitar errores circulares
from app import routes
from app import models