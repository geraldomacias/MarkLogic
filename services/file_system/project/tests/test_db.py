# services/users/project/tests/test_db.py

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