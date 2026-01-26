from flask import render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, login_required, current_user
from app import db, limiter
from app.models import User
from app.services.sms import get_sms_provider
from .. import auth
import pyotp, qrcode, io, base64, secrets


@auth.route("/verify-2fa-login", methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def verify_2fa_login():
    if '2fa_user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        token = request.form.get('token')
        user = User.query.get(session['2fa_user_id'])
        
        if user and user.otp_secret:
            totp = pyotp.TOTP(user.otp_secret)
            is_valid_token = totp.verify(token)
            is_valid_backup = False

            if not is_valid_token and user.backup_codes:
                codes = user.backup_codes.split(",")
                if token in codes:
                    is_valid_backup = True
                    codes.remove(token)
                    user.backup_codes = ",".join(codes)
                    db.session.commit()

            if is_valid_token or is_valid_backup:
                login_user(user)
                session.pop('2fa_user_id', None)
                return redirect(url_for('main.dashboard'))
            else:
                flash('Código inválido.', 'danger')
    return render_template('auth_otp/verify_2fa.html')


@auth.route("/send-sms-verification")
@login_required
@limiter.limit("3 per minute")
def send_sms_verification():
    if not current_user.phone_number:
        flash('No tienes un número de teléfono registrado.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    if current_user.is_phone_verified:
        flash('Tu teléfono ya está verificado.', 'info')
        return redirect(url_for('main.dashboard'))

    sms_provider = get_sms_provider(current_app.config)
    result = sms_provider.send_verification_code(current_user.phone_number)
    
    if result.success:
        session['sms_validation_code'] = result.code
        flash(result.message, 'info')
    else:
        flash(result.message, 'danger')
        return redirect(url_for('main.dashboard'))
    
    return redirect(url_for('auth.verify_sms_page'))


@auth.route("/verify-sms", methods=['GET', 'POST'])
@login_required
def verify_sms_page():
    if request.method == 'POST':
        input_code = request.form.get('sms_code')
        stored_code = session.get('sms_validation_code')
        
        if input_code and stored_code and input_code == stored_code:
            current_user.is_phone_verified = True
            db.session.commit()
            session.pop('sms_validation_code', None)
            flash('¡Teléfono verificado exitosamente!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Código SMS incorrecto. Intenta de nuevo.', 'danger')
            
    return render_template('auth_otp/verify_sms.html')


@auth.route("/enable-2fa")
@login_required
def enable_2fa():
    if not current_user.otp_secret:
        secret = pyotp.random_base32()
        current_user.otp_secret = secret
        backup_codes = [secrets.token_hex(4) for _ in range(5)]
        current_user.backup_codes = ",".join(backup_codes)
        db.session.commit()
    
    totp = pyotp.TOTP(current_user.otp_secret)
    uri = totp.provisioning_uri(name=current_user.username, issuer_name="AuthPractice")
    
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return render_template('auth_otp/enable_2fa.html', qr_code=img_b64, secret=current_user.otp_secret, backup_codes=current_user.backup_codes.split(","))
