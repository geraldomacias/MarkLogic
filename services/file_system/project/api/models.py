# services/file_system/project/api/models.py

import jwt

import datetime

from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY

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

class S3InputFiles(db.Model):
    """
    Model for storing input files, urls, and status
    """
    __tablename__ = 's3_input'

    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    filename = db.Column(db.String(128))
    url = db.Column(db.String(128), unique=True)
    deleted = db.Column(db.Boolean, default=False)

    db.UniqueConstraint('user_id', 'filename')

    def __init__(self, user_id, filename, url):
        self.user_id = user_id
        self.filename = filename
        self.url = url

class S3ClassifiedFiles(db.Model):
    """
    Model for storing classified files, urls, status, and foreign input files
    """
    __tablename__ = 's3_classified'

    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    filename = db.Column(db.String(128))
    url = db.Column(db.String(128), unique=True)
    deleted = db.Column(db.Boolean, default=False)
    input_files = db.Column(ARRAY(db.Integer, db.ForeignKey('S3InputFiles.file_id')))

    db.UniqueConstraint('user_id', 'filename')

    # INPUT FILES IS A LIST OF FILE_ID REFERENCES, FROM S3INPUTFILES TABLE
    def __init__(self, user_id, filename, url, input_files):
        self.user_id = user_id
        self.filename = filename
        self.url = url 
        self.input_files = input_files
