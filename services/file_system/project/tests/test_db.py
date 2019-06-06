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

# services/file_system/project/tests/test_db.py

import json
import unittest

from project import db
from project.api.models import BlacklistToken 
from project.tests.base import BaseTestCase 

class TestReadingBlacklistTokens(BaseTestCase):
    """Tests to make sure we can read BlasklistTokens created from users service"""

    def test_valid_blacklisted_token_logout(self):
        """Test for logout after valid token gets blacklisted"""

        blacklist_token = BlacklistToken('lolol')
        db.session.add(blacklist_token)
        db.session.commit()
        
        self.assertTrue(BlacklistToken.query.filter_by(token='lolol').first())
