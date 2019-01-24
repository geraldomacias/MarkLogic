# services/users/project/config.py

import os

class BaseConfig:
    """Base Configuration"""
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'my_precious')
    BCRYPT_LOG_ROUNDS = 13
    AUTH_EXPIRATION_SECONDS = 7200

class DevelopmentConfig(BaseConfig):
    """Development Configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    BCRYPT_LOG_ROUNDS = 4

class TestingConfig(BaseConfig):
    """Testing Configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')
    SECRET_KEY = 'my_precious'
    BCRYPT_LOG_ROUNDS = 4
    AUTH_EXPIRATION_SECONDS = 5

class ProductionConfig(BaseConfig):
    """Production Configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
