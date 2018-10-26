# pylint: disable=W0223,W0221,broad-except

from codebase.web import APIRequestHandler
from codebase.models import User


class UserHandler(APIRequestHandler):

    def post(self):
        """创建用户
        """
        body = self.get_body_json()

        user = self.db.query(User).filter_by(username=body["username"]).first()
        if user:
            self.fail("username-exist")
            return

        user = User(
            username=body["username"],
            password=body["password"],
        )
        self.db.add(user)
        self.db.commit()
        self.success(id=str(user.uuid))
