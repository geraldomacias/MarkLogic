"""
Copyright 2019 Team Mark

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# services/users/project/tests/test_config.py

import os
import unittest
import warnings

from flask import current_app
from flask_testing import TestCase

from project import create_app

app = create_app()

class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(app.config['SECRET_KEY'] != '')
        self.assertFalse(current_app is None)
        self.assertFalse(app.config['TESTING'])
        self.assertTrue(app.config['SQLALCHEMY_DATABASE_URI'] == os.environ.get('DATABASE_URL'))
        self.assertTrue(app.config['AUTH_EXPIRATION_SECONDS'] == 7200)

class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertTrue(app.config['SECRET_KEY'] == 'my_precious')
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertTrue(app.config['SQLALCHEMY_DATABASE_URI'] == os.environ.get('DATABASE_TEST_URL'))
        self.assertTrue(app.config['AUTH_EXPIRATION_SECONDS'] == 5)

class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.ProductionConfig')
        return app

    def test_app_is_production(self):
        try:
            self.assertTrue(app.config.get('SECRET_KEY') != 'my_precious')
        except AssertionError as e:
            warnings.warn('SECRET_KEY is not set!')
        self.assertFalse(app.config['TESTING'])
        self.assertTrue(app.config['SQLALCHEMY_DATABASE_URI'] == os.environ.get('DATABASE_URL'))
        self.assertTrue(app.config['AUTH_EXPIRATION_SECONDS'] == 7200)

if __name__ == '__main__':
    unittest.main()