import datetime

from eva.conf import settings

from codebase.models import User
from codebase.utils.token import gen_token, decode_token
from ..base import BaseTestCase


class NotApiTestCase(BaseTestCase):
    """Token
    """

    def test_gen_token(self):
        """gen_token
        """
        user = User(username="username", password="password")
        self.db.add(user)
        self.db.commit()

        expires_in = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=int(settings.APP_ACCESS_TOKEN_AGE)
        )
        tok = gen_token(user, expired=expires_in)

        payload = decode_token(tok)
        self.assertEqual(str(user.uuid), payload["uid"])
