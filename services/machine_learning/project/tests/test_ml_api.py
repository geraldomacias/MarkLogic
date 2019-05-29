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

# services/machine_learning/project/tests/test_ml_api.py

import json
import unittest
import time
import datetime
import jwt

from project import db 
from project.api.models import BlacklistToken, MLStatus, decode_auth_token
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

    def test_startml_no_status(self):
        """Test for starting ml with no status in status db."""
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

    def test_startml_bad_status(self):
        """Test for starting ml with status that isn't 'Waiting for files.'"""
        with self.client:
            auth_token = encode_auth_token(1)
            # set user status in db
            status = MLStatus(1, "Processing.")
            db.session.add(status)
            db.session.commit()
            # request
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
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Already processing files for this user.')
            self.assertEqual(response.status_code, 401)

    def test_startml(self):
        """Test for starting ml with correct status."""
        with self.client:
            auth_token = encode_auth_token(1)
            # set user status in db
            status = MLStatus(1, "Waiting for files.")
            db.session.add(status)
            db.session.commit()
            # request
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

class TestStatusML(BaseTestCase):
    """Tests to ensure ML Status works."""

    def test_statustml_no_auth(self):
        """Test for ml status with no provided token"""
        with self.client:
            response = self.client.get(
                '/ml/status'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Provide a valid auth token.')
            self.assertEqual(response.status_code, 401)

    def test_statusml_malformed_bearer(self):
        """Test for ml status with malformed bearer token."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.get(
                '/ml/status',
                headers=dict(
                    Authorization='Bearer' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Bearer token malformed.')
            self.assertEqual(response.status_code, 401)

    def test_statusml_blacklisted_token(self):
        """Test for ml status with a blacklisted token."""
        with self.client:
            auth_token = encode_auth_token(1)
            # Blacklist a valid token
            blacklist_token = BlacklistToken(auth_token.decode())
            db.session.add(blacklist_token)
            db.session.commit()
            # blacklisted token request
            response = self.client.get(
                '/ml/status',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_statusml_expired_token(self):
        """Test for ml status with an expired token."""
        with self.client:
            auth_token = encode_auth_token(1)
            # wait for token to be invalidated
            time.sleep(6)
            response = self.client.get(
                '/ml/status',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Signature expired. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_statusml_no_status(self):
        """Test for ml status with no previous status."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.get(
                '/ml/status',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Waiting for files.')
            self.assertEqual(response.status_code, 200)

    def test_statusml(self):
        """Test for ml status."""
        with self.client:
            auth_token = encode_auth_token(1)
            # insert ml status
            status = MLStatus(1, "Processing.")
            db.session.add(status)
            db.session.commit()
            # request
            response = self.client.get(
                '/ml/status',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Processing.')
            self.assertEqual(response.status_code, 200)

class TestGetClassified(BaseTestCase):
    """Tests to ensure getting classifed JSON workds."""

    def test_getclassified_no_auth(self):
        """Test for getting classified json with no provided token"""
        with self.client:
            response = self.client.get(
                '/ml/classified'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Provide a valid auth token.')
            self.assertEqual(response.status_code, 401)

    def test_getclassified_malformed_bearer(self):
        """Test for getting classified json with malformed bearer token."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.get(
                '/ml/classified',
                headers=dict(
                    Authorization='Bearer' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Bearer token malformed.')
            self.assertEqual(response.status_code, 401)

    def test_getclassified_blacklisted_token(self):
        """Test for getting classified json with blacklisted token."""
        with self.client:
            auth_token = encode_auth_token(1)
            # Blacklist a valid token
            blacklist_token = BlacklistToken(auth_token.decode())
            db.session.add(blacklist_token)
            db.session.commit()
            # blacklisted token request
            response = self.client.get(
                '/ml/classified',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_getclassified_expired_token(self):
        """Test for getting classified json with expired token."""
        with self.client:
            auth_token = encode_auth_token(1)
            # wait for token to be invalidated
            time.sleep(6)
            response = self.client.get(
                'ml/classified',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Signature expired. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_getclassified_no_status(self):
        """Test for getting classified json with no previous status."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.get(
                'ml/classified',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'User has not classified any data.')
            self.assertTrue(response.status_code, 404)

    def test_getclassified_wrong_status(self):
        """Test for getting classified json with status other than 'Completed.'"""
        with self.client:
            auth_token = encode_auth_token(1)
            # insert ml status
            status = MLStatus(1, "Processing.")
            db.session.add(status)
            db.session.commit()
            # request
            response = self.client.get(
                '/ml/classified',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Classification not yet completed for given user. Current status: Processing.')
            self.assertEqual(response.status_code, 401)

    def test_getclassified_no_json(self):
        """Test for getting classified json with no json in db."""
        with self.client:
            auth_token = encode_auth_token(1)
            # insert ml status
            status = MLStatus(1, "Completed.")
            db.session.add(status)
            db.session.commit()
            # request
            response = self.client.get(
                '/ml/classified',
                headers=dict(
                    Authorization='bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'No classified data found for given user.')
            self.assertEqual(response.status_code, 404)

    def test_getclassified(self):
        """Test for getting classified json."""
        with self.client:
            auth_token = encode_auth_token(1)
            # insert ml status
            status = MLStatus(1, "Completed.")
            status.classified_json = {
                'omg': '123'
            }
            db.session.add(status)
            db.session.commit()
            # request
            response = self.client.get(
                '/ml/classified',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            json_data = data['data']
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Returning classified information.')
            self.assertTrue(json_data['omg'] == '123')
            self.assertEqual(response.status_code, 200)

class TestGetPastClassifiedAsJson(BaseTestCase):
    """Tests to ensure getting past classifications as json works."""

    def test_getpastclassifiedasjson_no_auth(self):
        """Test for getting past classified json with no provided token"""
        with self.client:
            response = self.client.post(
                '/ml/past_classified_json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Provide a valid auth token.')
            self.assertEqual(response.status_code, 401)

    def test_getpastclassifiedasjson_malformed_bearer(self):
        """Test for getting past classified json with malformed bearer token."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.post(
                '/ml/past_classified_json',
                headers=dict(
                    Authorization='Bearer' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Bearer token malformed.')
            self.assertEqual(response.status_code, 401)

    def test_getpastclassifiedasjson_blacklisted_token(self):
        """Test for getting past classified json with blacklisted token."""
        with self.client:
            auth_token = encode_auth_token(1)
            # Blacklist a valid token
            blacklist_token = BlacklistToken(auth_token.decode())
            db.session.add(blacklist_token)
            db.session.commit()
            # blacklisted token request
            response = self.client.post(
                '/ml/past_classified_json',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_getpastclassifiedasjson_expired_token(self):
        """Test for getting past classified json with expired token."""
        with self.client:
            auth_token = encode_auth_token(1)
            # wait for token to be invalidated
            time.sleep(6)
            response = self.client.post(
                '/ml/past_classified_json',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Signature expired. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_getpastclassifiedasjson_no_files(self):
        """Test for getting past classified json with no json data provided."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.post(
                '/ml/past_classified_json',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'File name not provided.')
            self.assertTrue(response.status_code, 400)

    def test_getpastclassifiedasjson_bad_filename(self):
        """Test for getting past classified json with no 'file_name' key provided."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.post(
                '/ml/past_classified_json',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                ),
                data=json.dumps(dict(
                    test='bad'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'File name not provided.')
            self.assertEqual(response.status_code, 400)

    def test_getpastclassifiedasjson_bad_download_url(self):
        """Test for getting past classified json with bad generated url."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.post(
                '/ml/past_classified_json',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                ),
                data=json.dumps(dict(
                    file_name='bad_download_code'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Bad response from download url. Please try downloading again, or classify your csv again.')
            self.assertEqual(response.status_code, 404)

    def test_getpastclassifiedasjson(self):
        """Test for getting past classified json."""
        with self.client:
            auth_token = encode_auth_token(1)
            response = self.client.post(
                '/ml/past_classified_json',
                headers=dict(
                    Authorization='Bearer ' + auth_token.decode()
                ),
                data=json.dumps(dict(
                    file_name='test'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            json_data = data['data']
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Returning classified information.')
            self.assertTrue(json_data['test_data'] == 123)
            self.assertEqual(response.status_code, 200)