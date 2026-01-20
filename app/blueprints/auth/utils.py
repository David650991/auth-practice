from flask import url_for
from flask_mail import Message
from app import mail

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender='noreply@tuseguridad.com'
    )
    mail.send(msg)

def send_confirmation_email(user):
    token = user.get_token(salt='email-confirm-salt')
    link = url_for('auth.confirm_email', token=token, _external=True)
    html_body = f'''
    <h1>Bienvenido, {user.username}</h1>
    <p>Gracias por registrarte. Para activar tu cuenta, por favor confirma tu correo:</p>
    <a href="{link}" style="padding:10px; background:blue; color:white;">CONFIRMAR MI CORREO</a>
    <p>O copia este enlace: {link}</p>
    '''
    send_email(user.email, 'Confirma tu Cuenta', html_body)

def send_reset_email(user):
    token = user.get_token(salt='password-reset-salt')
    link = url_for('auth.reset_token', token=token, _external=True)
    html_body = f'''
    <h1>Recuperación de Acceso</h1>
    <p>Para restablecer tu contraseña, haz clic aquí:</p>
    <a href="{link}" style="padding:10px; background:red; color:white;">RESTABLECER CONTRASEÑA</a>
    <p>Si no fuiste tú, ignora este mensaje.</p>
    '''
    send_email(user.email, 'Solicitud de Cambio de Contraseña', html_body)