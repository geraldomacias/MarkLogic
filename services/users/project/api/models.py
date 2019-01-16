# services/users/project/api/models.py

import datetime

import jwt

from sqlalchemy.sql import func

from project import db, bcrypt

from flask import current_app

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    last_login_date = db.Column(db.DateTime, default=func.now(), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, current_app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.created_date = datetime.datetime.now()
        self.last_login_date = self.created_date

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        returns a string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=current_app.config.get('AUTH_EXPIRATION_SECONDS')),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e
    
    def update_login_date(self):
        """
        Updates the last_login_date field for the user
        """
        self.last_login_date = datetime.datetime.now()
        db.session.commit()
    
    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        returns integer or string
        """
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'