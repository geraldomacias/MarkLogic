# services/file_system/project/config.py

import os

class BaseConfig:
    """Base Configuration"""
    TESTING = False
    SECRET_KEY = 'my_precious'

class DevelopmentConfig:
    """Development Configuration"""
    pass