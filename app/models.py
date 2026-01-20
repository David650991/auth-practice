from app import db, login_manager
from flask import current_app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=True) 
    password = db.Column(db.String(60), nullable=False)
    
    # Estados de confirmación
    confirmed = db.Column(db.Boolean, nullable=False, default=False) # Email
    confirmed_on = db.Column(db.DateTime, nullable=True)
    
    # NUEVO: Estado del Teléfono
    is_phone_verified = db.Column(db.Boolean, default=False) 

    # Seguridad 2FA
    otp_secret = db.Column(db.String(32), nullable=True)
    backup_codes = db.Column(db.String(250), nullable=True)

    def get_token(self, salt='default-salt'):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt=salt)

    @staticmethod
    def verify_token(token, salt='default-salt', expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt=salt, max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"