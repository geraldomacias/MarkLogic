# services/machine_learning/project/api/models.py

import jwt

import datetime

from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import JSON

from project import db

from flask import current_app

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

class MLStatus(db.Model):
    """
    Model for storing user ML status
    """
    __tablename__ = 'ml_status'

    user_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(128), nullable=False)
    error_msg = db.Column(db.String(128), nullable=True)
    selected_files = db.Column(ARRAY(db.String(128)), nullable=True)
    working_directory = db.Column(db.String(500), nullable=True)
    classified_json = db.Column(JSON, nullable=True)

    def __init__(self, user_id, status):
        self.user_id = user_id 
        self.status = status 
