from codebase.models import User
from codebase.utils.swaggerui import api

from .base import (
    BaseTestCase,
    validate_default_error,
    get_body_json
)


class _Base(BaseTestCase):

    rs = api.spec.resources["user"]


class UserCreateTestCase(_Base):
    """POST /user - 创建用户
    """

    def test_username_exist(self):
        """用户名已经存在
        """

        resp = self.api_post("/user", body={
            "username": self.current_username})
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "username-exist")

    def test_create_success(self):
        """创建成功
        """
        username = "for-ceate-test"
        password = "ffffff"
        resp = self.api_post("/user", body={
            "username": username,
            "password": password,
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        user = self.db.query(User).filter_by(username=username).one()
        self.assertEqual(user.validate_password(password), True)
