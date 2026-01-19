from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Configuración de Seguridad
app.config['SECRET_KEY'] = 'clave-secreta-temporal-para-desarrollo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Inicialización de Extensiones
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Inicialización del Escudo (Limiter)
# get_remote_address usa la IP del usuario para identificarlo
limiter = Limiter(
    get_remote_address, 
    app=app, 
    default_limits=["200 per day", "50 per hour"], # Límite general suave
    storage_uri="memory://" # Guardamos los conteos en memoria RAM por velocidad
)

# Importamos rutas y modelos al final
from app import routes
from app import models