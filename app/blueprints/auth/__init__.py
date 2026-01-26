from flask import Blueprint

# 1. Creamos el Blueprint 'auth' aquí
auth = Blueprint('auth', __name__)

# 2. Importamos las rutas por contexto (mantiene los mismos endpoints)
# Es IMPORTANTE que esto esté al final para evitar errores de importación circular
from .auth_password import routes as auth_password_routes
from .auth_otp import routes as auth_otp_routes
from .auth_biometric import routes as auth_biometric_routes