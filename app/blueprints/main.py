from flask import Blueprint, render_template
from flask_login import login_required, current_user

# Definimos el Blueprint 'main'
main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')

@main.route("/dashboard")
@login_required
def dashboard():
    # Lógica para mostrar estado de 2FA basada en tus templates
    estado_2fa = "ACTIVADO" if current_user.otp_secret else "DESACTIVADO"
    return render_template('main/dashboard.html', usuario=current_user.username, estado_2fa=estado_2fa)