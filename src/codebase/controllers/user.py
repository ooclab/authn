# pylint: disable=W0223,W0221,broad-except

import datetime

from tornado.web import HTTPError
from sqlalchemy import and_

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
            password=body.get("password"),
        )
        self.db.add(user)
        self.db.commit()
        self.success(id=str(user.uuid))


class _BaseSingleUserHandler(APIRequestHandler):

    def get_user(self, _id):
        user = self.db.query(User).filter_by(uuid=_id).first()
        if not user:
            raise HTTPError(400, reason="not-found")
        return user


class SingleUserHandler(_BaseSingleUserHandler):

    def get(self, _id):
        """获取用户详情
        """
        user = self.get_user(_id)
        self.success(data=user.ifull)

    def post(self, _id):
        """更新用户属性
        """
        user = self.get_user(_id)
        body = self.get_body_json()

        username = body.get("username")
        password = body.get("password")
        is_active = body.get("is_active")
        if username:
            username = body.pop("username")
            exist_user = self.db.query(User).filter(
                and_(User.username == username, User.id != user.id)).first()
            if exist_user:
                self.fail("username-exist")
                return
            user.username = username
        if password:
            user.set_password(password)
        has_is_active = is_active in [False, True]
        if has_is_active:
            user.is_active = is_active
        if username or password or has_is_active:
            user.updated = datetime.datetime.utcnow()
            self.db.commit()

        self.success()

    def delete(self, _id):
        """删除用户
        """
        user = self.get_user(_id)
        self._remove_user(user)
        self.success()

    def _remove_user(self, user):
        # TODO: 真的要完全删除该用户吗？
        for app in user.apps:
            self.db.delete(app)

        user.apps = []

        # 删除自身
        self.db.delete(user)

        self.db.commit()
