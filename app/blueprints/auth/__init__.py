from flask import Blueprint

# 1. Creamos el Blueprint 'auth' aquí
auth = Blueprint('auth', __name__)

# 2. Importamos las rutas (vistas) para que se registren en el Blueprint
# Es IMPORTANTE que esto esté al final para evitar errores de importación circular
from . import routes_auth, routes_security