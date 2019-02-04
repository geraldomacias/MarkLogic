# services/users/project/api/test_ml_api.py

import json
import unittest
import time
import datetime
import jwt

from project import db 
from project.api.models import BlacklistToken, decode_auth_token
from project.tests.base import BaseTestCase

from flask import current_app

def encode_auth_token(user_id):
    """
    Generates the Auth Token (for testing only)
    returns a string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
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

class TestJWT(BaseTestCase):
    """Tests to ensure encoding / decoding JWT works."""

    def test_encode_auth_token(self):
        """Ensure auth tokens are encoded correctly."""
        auth_token = encode_auth_token(1)
        self.assertTrue(isinstance(auth_token, bytes))
    
    def test_decode_auth_token(self):
        """Ensure auth tokens are decoded correctly."""
        auth_token = encode_auth_token(1)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(decode_auth_token(auth_token.decode("utf-8")) == 1)

class TestStartML(BaseTestCase):
    """Tests to ensure starting the ML component works."""

    def test_startml_no_auth(self):
        """Test for starting ml with no provided token"""
        with self.client:
            response = self.client.post(
                '/ml/start'
            )
            data=json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Provide a valid auth token.')
            self.assertEqual(response.status_code, 401)
    
    def test_startml_malformed_bearer(self):
        """Test for starting ml with malformed bearer token."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.post(
                '/ml/start',
                headers=dict(
                    Authorization='Bearer' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Bearer token malformed.')
            self.assertEqual(response.status_code, 401)

    def test_startml_blacklisted_token(self):
        """Test for starting ml with a blacklisted token."""
        with self.client:
            auth_token = encode_auth_token(1)
            # Blacklist a valid token
            blacklist_token = BlacklistToken(auth_token.decode())
            db.session.add(blacklist_token)
            db.session.commit()
            # blacklisted token request
            response = self.client.post(
                '/ml/start',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_startml_expired_token(self):
        """Test for starting ml with an expired token."""
        with self.client:
            auth_token = encode_auth_token(1)
            # wait for token to be invalidated
            time.sleep(6)
            response = self.client.post(
                '/ml/start',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Signature expired. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_startml_no_files(self):
        """Test for starting ml with no provided files."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.post(
                '/ml/start',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'No files provided.')
            self.assertEqual(response.status_code, 400)

    def test_startml_empty_file_list(self):
        """Test for starting ml with an empty file list."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.post(
                '/ml/start',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                ),
                data=json.dumps(dict(
                    files=[]
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'No files provided.')
            self.assertEqual(response.status_code, 400)

    def test_startml(self):
        """Test for starting ml with correct input."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.post(
                '/ml/start',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                ),
                data=json.dumps(dict(
                    files=['file_1', 'file_2']
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully started ML on 2 files.')
            self.assertEqual(response.status_code, 200)
