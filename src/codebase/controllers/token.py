# pylint: disable=W0221,W0223

import datetime

from tornado.web import HTTPError
from eva.conf import settings
from eva.utils.time_ import utc_rfc3339_string

from codebase.models import (
    App,
    User,
    UserSession,
    AppSession
)
from codebase.utils.token import gen_token
from codebase.web import APIRequestHandler


def clean_session(db, user):
    # 清理 sessions
    # TODO: 是清理还是禁止登录？

    # FIXME: 不能混合删除，需要综合考虑
    sessions = []
    sessions.extend(user.sessions)
    for app in user.apps:
        sessions.extend(app.sessions)

    for i, session in enumerate(sessions):
        if session.is_expired:
            db.delete(session)
            continue
        # 限制 refresh_token 数量
        # TODO: 清理顺序应该是清理最新的还是最旧的？
        if i >= int(settings.MAX_SESSION_PER_USER) - 1:
            db.delete(session)


class UserTokenHandler(APIRequestHandler):

    def post(self):
        """用户登录"""
        body = self.get_body_json()

        username = body["username"]
        password = body["password"]

        user = self.db.query(User).filter_by(username=username).first()

        # 错误用户名
        if not user:
            self.fail("username-or-password-incorrect")
            return

        # 错误密码
        if not user.validate_password(password):
            self.fail("username-or-password-incorrect")
            return

        # 账号已被禁用
        if not user.is_active:
            self.fail("user-inactive")
            return

        # 验证成功
        expires_in = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=int(settings.USER_ACCESS_TOKEN_AGE)
        )
        clean_session(self.db, user)
        session = UserSession(user)
        self.db.add(session)
        self.db.commit()

        self.success(data={
            "uid": str(user.uuid),
            "access_token": gen_token(user, expires_in),
            "expires_in": utc_rfc3339_string(expires_in),
            "refresh_token": session.refresh_token,
        })


class UserTokenRefreshHandler(APIRequestHandler):

    def post(self):
        """
        用户通过 refresh_token 获取新的 access_token
        """
        body = self.get_body_json()
        refresh_token = body["refresh_token"]

        session = self.db.query(UserSession).filter_by(
            refresh_token=refresh_token).first()
        if not session:
            self.fail("invalid-refresh-token")
            return

        if session.is_expired:
            self.fail("is-expired")
            return

        user = session.user

        # TODO: 有可能用户已经被禁用（忘记删除 session）
        if not user.is_active:
            self.fail("user-inactive")
            return

        clean_session(self.db, user)

        # 验证成功
        expires_in = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=int(settings.USER_ACCESS_TOKEN_AGE)
        )

        # TODO: 如果用户的 refresh_token 还未过期（至少到下一次需要刷新时），无需新建
        if session.expires_in < expires_in:
            self.db.delete(session)
            session = UserSession(user)
            self.db.add(session)
            self.db.commit()

        self.success(data={
            "uid": str(user.uuid),
            "access_token": gen_token(user, expires_in),
            "expires_in": utc_rfc3339_string(expires_in),
            "refresh_token": session.refresh_token,
        })


class _BaseSingleAppHandler(APIRequestHandler):

    def get_app(self, _id):
        app = self.db.query(App).filter_by(app_id=_id).first()
        if not app:
            raise HTTPError(400, reason="incorrect-app-id")
        return app


class SingleAppTokenHandler(_BaseSingleAppHandler):

    def post(self):
        """App “登录”
        """
        body = self.get_body_json()
        app_id = body["app_id"]
        app = self.get_app(app_id)
        app_secret = body["app_secret"]

        # 错误的 api_secret
        if not app.validate_secret(app_secret):
            self.fail("incorrect-app-id-or-secret")
            return

        # App 已被禁用
        if not app.is_active:
            self.fail("app-inactive")
            return

        user = app.user

        # 用户被禁用
        if not user.is_active:
            self.fail("user-inactive")
            return

        # 验证成功
        expires_in = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=int(settings.APP_ACCESS_TOKEN_AGE)
        )
        clean_session(self.db, user)
        session = AppSession(app)
        self.db.add(session)
        self.db.commit()

        self.success(data={
            "uid": str(user.uuid),
            "access_token": gen_token(user, expires_in),
            "expires_in": utc_rfc3339_string(expires_in),
            "refresh_token": session.refresh_token,
        })


class SingleAppTokenRefreshHandler(_BaseSingleAppHandler):

    def post(self):
        """
        应用通过 refresh_token 获取新的 access_token
        """
        body = self.get_body_json()
        app_id = body["app_id"]
        refresh_token = body["refresh_token"]
        app = self.get_app(app_id)

        session = self.db.query(AppSession).filter_by(
            refresh_token=refresh_token).first()
        if not session:
            self.fail("invalid-refresh-token")
            return

        if session.is_expired:
            self.fail("is-expired")
            return

        app = session.app
        user = app.user

        if not app.is_active:
            self.fail("app-inactive")
            return

        # TODO: 有可能用户已经被禁用（忘记删除 session）
        if not user.is_active:
            self.fail("user-inactive")
            return

        clean_session(self.db, user)

        # 验证成功
        expires_in = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=int(settings.APP_ACCESS_TOKEN_AGE)
        )

        # TODO: 如果用户的 refresh_token 还未过期（至少到下一次需要刷新时），无需新建
        if session.expires_in < expires_in:
            session = AppSession(app)
            self.db.add(session)
            self.db.commit()

        self.success(data={
            "uid": str(user.uuid),
            "access_token": gen_token(user, expires_in),
            "expires_in": utc_rfc3339_string(expires_in),
            "refresh_token": session.refresh_token,
        })
