from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt  # <--- CORREGIDO: Importamos Bcrypt, no FlaskBcrypt
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicialización de extensiones
db = SQLAlchemy()
bcrypt = Bcrypt()  # <--- CORREGIDO: Inicializamos Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-default')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones con la app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # Importar y registrar Blueprints
    from app.blueprints.main import main
    from app.blueprints.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app