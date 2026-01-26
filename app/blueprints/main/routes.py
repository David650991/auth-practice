from flask import render_template
from flask_login import login_required, current_user

from . import main


@main.route("/")
@main.route("/home")
def home():
    return render_template('main/home.html')


@main.route("/dashboard")
@login_required
def dashboard():
    estado_2fa = "ACTIVADO" if current_user.otp_secret else "DESACTIVADO"
    return render_template('main/dashboard.html', usuario=current_user.username, estado_2fa=estado_2fa)
