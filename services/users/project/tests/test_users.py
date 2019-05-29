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

# services/users/project/tests/test_users.py

import json
import unittest
import time

from project import db
from project.api.models import User, BlacklistToken
from project.tests.base import BaseTestCase

def add_user(email, password):
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return user

def register_user(self, email, password):
    return self.client.post(
        '/users/register',
        data=json.dumps(dict(
            email=email,
            password=password
        )),
        content_type='application/json'
    )

def login_user(self, email, password):
    return self.client.post(
        '/users/login',
        data=json.dumps(dict(
            email=email,
            password=password
        )),
        content_type='application/json'
    )

class TestUserModel(BaseTestCase):
    """Tests for the Users Model."""

    def test_encode_auth_token(self):
        """Ensure auth tokens are encoded correctly."""
        user = add_user('test@test.com', 'test')
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        """Ensure auth tokens are decoded correctly."""
        user = add_user('test@test.com', 'test')
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(User.decode_auth_token(auth_token.decode("utf-8")) == 1)


class TestUserService(BaseTestCase):
    """Tests for the Users Service."""

    def test_registration(self):
        """Test for user registration."""
        with self.client:
            response = register_user(self, 'spencer.schurk@gmail.com', '123456')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_registered_with_already_registered_user(self):
        """Test registration with already registered email"""
        user = add_user('spencer.schurk@gmail.com', 'test')
        with self.client:
            response = register_user(self, 'spencer.schurk@gmail.com', '123456')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'User already exists. Please log in.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 202)

    def test_registration_invalid_email(self):
        """Test registration with an invalid email address"""
        with self.client:
            response = register_user(self, 'bademail@lmfao', '123456')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Email is not valid.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 400)

    def test_registered_user_login(self):
        """Test for login of registered user"""
        with self.client:
            # user registration
            resp_register = register_user(self, 'spencer.schurk@gmail.com', '123456')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.'
            )
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # registered user login
            response = login_user(self, 'spencer.schurk@gmail.com', '123456')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_non_registered_user_login(self):
        """Test for login of non-registered user"""
        with self.client:
            response = login_user(self, 'spencer.schurk@gmail.com', '123456')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'User does not exist.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_registered_user_wrong_password(self):
        """Test for login of registered user with incorrect password"""
        with self.client:
            # user registration
            resp_register = register_user(self, 'spencer.schurk@gmail.com', '123456')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.'
            )
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # registered user login
            response = login_user(self, 'spencer.schurk@gmail.com', 'test')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Password is incorrect.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 401)

    def test_user_status(self):
        """Test for user status"""
        with self.client:
            resp_register = register_user(self, 'spencer.schurk@gmail.com', '123456')
            response = self.client.get(
                '/users/status',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_register.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['data'] is not None)
            self.assertTrue(data['data']['email'] == 'spencer.schurk@gmail.com')
            self.assertEqual(response.status_code, 200)
    
    def test_last_login_updated(self):
        """Test to ensure last_login_date is being updated"""
        with self.client:
            resp_register = register_user(self, 'spencer.schurk@gmail.com', '123456')
            time.sleep(1)
            login_user(self, 'spencer.schurk@gmail.com', '123456')
            response = self.client.get(
                '/users/status',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_register.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['data']['last_login_date'] is not None)
            self.assertTrue(data['data']['last_login_date'] > data['data']['created_date'])

    def test_valid_logout(self):
        """Test for logout before token expires"""
        with self.client:
            # user registration
            resp_register = register_user(self, 'spencer.schurk@gmail.com', '123456')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # user login
            resp_login = login_user(self, 'spencer.schurk@gmail.com', '123456')
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['message'] == 'Successfully logged in.')
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)
            # valid token logout
            response = self.client.post(
                '/users/logout',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged out.')
            self.assertEqual(response.status_code, 200)

    def test_invalid_logout(self):
        """Test for logout after token expires"""
        with self.client:
            # user registration
            resp_register = register_user(self, 'spencer.schurk@gmail.com', '123456')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # user login
            resp_login = login_user(self, 'spencer.schurk@gmail.com', '123456')
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['message'] == 'Successfully logged in.')
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)
            # invalid token logout
            time.sleep(6)
            response = self.client.post(
                '/users/logout',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'Signature expired. Please log in again.')
            self.assertEqual(response.status_code, 401)
    
    def test_valid_blacklisted_token_logout(self):
        """Test for logout after valid token gets blacklisted"""
        with self.client:
            # user registration
            resp_register = register_user(self, 'spencer.schurk@gmail.com', '123456')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # user login
            resp_login = login_user(self, 'spencer.schurk@gmail.com', '123456')
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['message'] == 'Successfully logged in.')
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)
            # blacklist a valid token
            blacklist_token = BlacklistToken(
                token=json.loads(resp_login.data.decode())['auth_token'])
            db.session.add(blacklist_token)
            db.session.commit()
            # blacklisted valid token logout
            response = self.client.post(
                '/users/logout',
                headers=dict(
                    Authorization="Bearer " + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_valid_blacklisted_token_user(self):
        """Test for user status with a blacklsited valid token"""
        with self.client:
            resp_register = register_user(self, 'spencer.schurk@gmail.com', '123456')
            # blacklist a valid token
            blacklist_token = BlacklistToken(
                token=json.loads(resp_register.data.decode())['auth_token'])
            db.session.add(blacklist_token)
            db.session.commit()
            response = self.client.get(
                '/users/status',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_register.data.decode()
                    )['auth_token']
                )
            )
            data=json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_user_status_malformed_bearer_token(self):
        """Test for user status with malformed bearer token"""
        with self.client:
            resp_register = register_user(self, 'spencer.schurk@gmail.com', '123456')
            response = self.client.get(
                '/users/status',
                headers=dict(
                    Authorization='Bearer' + json.loads(
                        resp_register.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Bearer token malformed.')
            self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()