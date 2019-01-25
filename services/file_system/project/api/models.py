# services/file_system/project/api/models.py

import jwt

import datetime

from sqlalchemy.sql import func

from project import db

from flask import current_app

@staticmethod
def decode_auth_token(auth_token):
    """
    Decodes the auth token
    returns integer or string
    """
    try:
        payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
        is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
        if is_blacklisted_token:
            return 'Token blacklisted. Please log in again.'
        else:
            return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False

class S3Files(db.Model):
    """
    Model for storing files and their corresponding urls
    """
    __tablename__ = 's3_files'

    user_id = db.Column(db.Integer, primary_key=True)
    input_filename = db.Column(db.String(128), nullable=False, primary_key=True)
    input_url = db.Column(db.String(128), unique=True, nullable=False)
    classified_filename = db.Column(db.String(128), nullable=True)
    classified_url = db.Column(db.String(128), nullable=True)

    def __init__(self, user_id, input_filename, input_url):
        self.user_id = user_id
        self.input_filename = input_filename
        self.input_url = input_url