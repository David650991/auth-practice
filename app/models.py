from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # NUEVA COLUMNA: Aquí guardaremos el secreto del Authenticator
    otp_secret = db.Column(db.String(32), nullable=True) 

    def __repr__(self):
        return f"User('{self.username}')"