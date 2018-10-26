import datetime
import uuid

from codebase.models import (
    User,
    App,
    UserSession,
    AppSession
)
from codebase.utils.swaggerui import api
from codebase.utils.token import decode_token


from .base import (
    BaseTestCase,
    validate_default_error,
    get_body_json
)


class _Base(BaseTestCase):

    rs = api.spec.resources["token"]


class UserCreateToken(_Base):
    """POST /user/token - 用户获取 access_token
    """

    def test_username_invalid(self):
        """用户名错误
        """

        resp = self.api_post("/user/token", body={
            "username": "notexist",
            "password": "password",
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "username-or-password-incorrect")

    def test_password_invalid(self):
        """密码错误
        """
        resp = self.api_post("/user/token", body={
            "username": self.current_user.username,
            "password": "wrong",
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "username-or-password-incorrect")

    def test_user_inactive(self):
        """用户被禁用
        """
        self.current_user.is_active = False
        self.db.commit()
        resp = self.api_post("/user/token", body={
            "username": self.current_username,
            "password": self.current_password,
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "user-inactive")

    def test_get_token_success(self):
        """获取 token 成功
        """
        resp = self.api_post("/user/token", body={
            "username": self.current_username,
            "password": self.current_password,
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.post_user_token.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        data = body["data"]
        payload = decode_token(data["access_token"])
        self.assertEqual(payload["uid"], str(self.current_user.uuid))


class UserGetTokenRefresh(_Base):
    """GET /user/token/refresh - 用户刷新 access_token
    """

    def test_refresh_token_invalid(self):
        """无效的 refresh token
        """

        for token in [None, "", "notexist"]:
            resp = self.api_get(f"/user/token/refresh?refresh_token={token}")
            body = get_body_json(resp)
            self.assertEqual(resp.code, 400)
            validate_default_error(body)
            self.assertEqual(body["status"], "invalid-refresh-token")

    def test_session_is_expired(self):
        """会话过期
        """

        resp = self.api_post("/user/token", body={
            "username": self.current_username,
            "password": self.current_password,
        })
        body = get_body_json(resp)
        refresh_token = body["data"]["refresh_token"]
        session = self.db.query(UserSession).filter_by(
            refresh_token=refresh_token).first()
        session.expires_in = datetime.datetime.utcnow()
        self.db.commit()

        resp = self.api_get(f"/user/token/refresh?refresh_token={refresh_token}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "is-expired")

    def test_user_inactive(self):
        """用户被禁用
        """
        resp = self.api_post("/user/token", body={
            "username": self.current_username,
            "password": self.current_password,
        })
        body = get_body_json(resp)
        refresh_token = body["data"]["refresh_token"]

        # TODO: 为什么需要删除再获取？
        del self.current_user
        self.current_user = self.db.query(User).filter_by(
            username=self.current_username).first()
        self.current_user.is_active = False
        self.db.commit()

        resp = self.api_get(f"/user/token/refresh?refresh_token={refresh_token}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "user-inactive")

    def test_refresh_token_success(self):
        """刷新成功
        """
        resp = self.api_post("/user/token", body={
            "username": self.current_username,
            "password": self.current_password,
        })
        body = get_body_json(resp)
        refresh_token = body["data"]["refresh_token"]

        resp = self.api_get(f"/user/token/refresh?refresh_token={refresh_token}")
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.get_user_token_refresh.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        data = body["data"]
        payload = decode_token(data["access_token"])
        self.assertEqual(payload["uid"], str(self.current_user.uuid))


class AppGetToken(_Base):
    """GET /app/{id}/token - App 获取 access_token
    """

    def test_app_id_invalid(self):
        """App ID 无效
        """
        app_id = str(uuid.uuid4())
        resp = self.api_get(f"/app/{app_id}/token")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "incorrect-app-id")

    def test_app_secret_invalid(self):
        """app_secret 错误
        """
        app = App(user=self.current_user, name="fortest", api_secret="secret")
        self.db.add(app)
        self.db.commit()

        resp = self.api_get(f"/app/{app.uuid}/token?api_secret=wrong")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "incorrect-app-id-or-secret")

    def test_user_inactive(self):
        """用户被禁用
        """
        self.current_user.is_active = False
        api_secret = "secret"
        app = App(user=self.current_user, name="fortest", api_secret=api_secret)
        self.db.add(app)
        self.db.commit()
        resp = self.api_get(f"/app/{app.uuid}/token?api_secret={api_secret}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "user-inactive")

    def test_app_inactive(self):
        """App 被禁用
        """
        api_secret = "secret"
        app = App(user=self.current_user, name="fortest", api_secret=api_secret)
        app.is_active = False
        self.db.add(app)
        self.db.commit()
        resp = self.api_get(f"/app/{app.uuid}/token?api_secret={api_secret}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "app-inactive")

    def test_get_token_success(self):
        """获取 token 成功
        """
        api_secret = "secret"
        app = App(user=self.current_user, name="fortest", api_secret=api_secret)
        self.db.add(app)
        self.db.commit()

        resp = self.api_get(f"/app/{app.uuid}/token?api_secret={api_secret}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.get_app_id_token.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        data = body["data"]
        payload = decode_token(data["access_token"])
        self.assertEqual(payload["uid"], str(self.current_user.uuid))


class AppGetTokenRefresh(_Base):
    """GET /app/{id}/token/refresh - App 刷新 access_token
    """

    def test_refresh_token_invalid(self):
        """无效的 refresh token
        """
        app = App(user=self.current_user, name="fortest", api_secret="secret")
        self.db.add(app)
        self.db.commit()

        for token in [None, "", "notexist"]:
            resp = self.api_get(f"/app/{app.uuid}/token/refresh?refresh_token={token}")
            body = get_body_json(resp)
            self.assertEqual(resp.code, 400)
            validate_default_error(body)
            self.assertEqual(body["status"], "invalid-refresh-token")

    def test_session_is_expired(self):
        """会话过期
        """
        api_secret = "secret"
        app = App(user=self.current_user, name="fortest", api_secret=api_secret)
        self.db.add(app)
        self.db.commit()
        app_id = str(app.uuid)

        resp = self.api_get(f"/app/{app_id}/token?api_secret={api_secret}")
        body = get_body_json(resp)
        refresh_token = body["data"]["refresh_token"]
        session = self.db.query(AppSession).filter_by(
            refresh_token=refresh_token).first()
        session.expires_in = datetime.datetime.utcnow()
        self.db.commit()

        resp = self.api_get(
            f"/app/{app_id}/token/refresh?refresh_token={refresh_token}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "is-expired")

    def test_user_inactive(self):
        """用户被禁用
        """
        api_secret = "secret"
        app = App(user=self.current_user, name="fortest", api_secret=api_secret)
        self.db.add(app)
        self.db.commit()
        app_id = str(app.uuid)

        resp = self.api_get(f"/app/{app_id}/token?api_secret={api_secret}")
        body = get_body_json(resp)
        refresh_token = body["data"]["refresh_token"]

        # TODO: 为什么需要删除再获取？
        del self.current_user
        self.current_user = self.db.query(User).filter_by(
            username=self.current_username).first()
        self.current_user.is_active = False
        self.db.commit()

        resp = self.api_get(
            f"/app/{app_id}/token/refresh?refresh_token={refresh_token}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "user-inactive")

    def test_refresh_token_success(self):
        """刷新成功
        """
        api_secret = "secret"
        app = App(user=self.current_user, name="fortest", api_secret=api_secret)
        self.db.add(app)
        self.db.commit()
        app_id = str(app.uuid)

        resp = self.api_get(f"/app/{app_id}/token?api_secret={api_secret}")
        body = get_body_json(resp)
        refresh_token = body["data"]["refresh_token"]

        resp = self.api_get(
            f"/app/{app_id}/token/refresh?refresh_token={refresh_token}")
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.get_user_token_refresh.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        data = body["data"]
        payload = decode_token(data["access_token"])
        self.assertEqual(payload["uid"], str(self.current_user.uuid))
