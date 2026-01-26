from flask import Blueprint

# Blueprint principal de vistas generales
main = Blueprint('main', __name__)

from . import routes  # noqa: E402,F401
