# services/file_system/project/tests/test_s3_api.py

import json
import unittest
import time
import datetime
import jwt

from project import db
from project.api.models import BlacklistToken, S3Files, decode_auth_token
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

class TestUploadedFiles(BaseTestCase):
    """Tests to ensure uploaded file list is returned correctly."""

    def test_uploaded_files_no_auth(self):
        """Test for getting uploaded files with no provided token."""
        with self.client:
            response = self.client.get(
                '/s3/file_list'
            )
            data=json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Provide a valid auth token.')
            self.assertEqual(response.status_code, 401)

    def test_uploaded_files_malformed_bearer(self):
        """Test for getting uploaded files with malformed bearer token."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.get(
                '/s3/file_list',
                headers=dict(
                    Authorization='Bearer' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Bearer token malformed.')
            self.assertEqual(response.status_code, 401)

    def test_uploaded_files_blacklisted_token(self):
        """Test for getting uploaded files with a blacklisted token."""
        with self.client:
            auth_token = encode_auth_token(1)
            # Blacklist a valid token
            blacklist_token = BlacklistToken(auth_token.decode())
            db.session.add(blacklist_token)
            db.session.commit()
            # blacklisted token request
            response = self.client.get(
                '/s3/file_list',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_uploaded_files_expired_token(self):
        """Test for getting uploaded files with an expired token."""
        with self.client:
            auth_token = encode_auth_token(1)
            # wait for token to be invalidated
            time.sleep(6)
            response = self.client.get(
                '/s3/file_list',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Signature expired. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_uploaded_files_no_uploaded_files(self):
        """Test for getting uploaded files with no user files."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.get(
                '/s3/file_list',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Listing 0 files.')
            self.assertEqual(response.status_code, 200)

    def test_uploaded_files(self):
        """Test for getting uploaded files with correct input."""
        with self.client:
            auth_token = encode_auth_token(1)
            # add two uploaded files to db
            file1 = S3Files(1, 'file1', 'file1_url')
            file2 = S3Files(1, 'file2', 'file2_url')
            db.session.add(file1)
            db.session.add(file2)
            db.session.commit()
            # request
            response = self.client.get(
                '/s3/file_list',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Listing 2 files.')
            self.assertTrue(len(data['data']) == 2)
            self.assertTrue(data['data'][0] == 'file1')
            self.assertTrue(data['data'][1] == 'file2')