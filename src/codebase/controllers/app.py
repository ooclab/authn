# pylint: disable=W0223,W0221,broad-except

import datetime

from sqlalchemy import and_
from tornado.web import HTTPError

from codebase.web import APIRequestHandler, authenticated
from codebase.models import App


class AppHandler(APIRequestHandler):

    @authenticated
    def get(self):
        """获取我的所有 App
        """
        self.success(data=[
            app.isimple
            for app in self.current_user.apps])

    @authenticated
    def post(self):
        """创建 App
        """
        body = self.get_body_json()

        name = body["name"]
        if self.db.query(App).filter(and_(
                App.name == name,
                App.user_id == self.current_user.id
        )).first():
            self.fail("name-exist")
            return

        app = App(
            user=self.current_user,
            name=name,
            app_secret=body["app_secret"],
            summary=body.get("summary"),
            description=body.get("description"),
            is_active=body.get("is_active")
        )
        self.db.add(app)
        self.db.commit()
        self.success(id=str(app.app_id))


class _BaseSingleAppHandler(APIRequestHandler):

    def get_app(self, _id):
        app = self.db.query(App).filter(and_(
            App.app_id == _id,
            App.user_id == self.current_user.id
        )).first()
        if not app:
            raise HTTPError(400, reason="not-found")
        return app


class SingleAppHandler(_BaseSingleAppHandler):

    @authenticated
    def get(self, _id):
        """获取我的 App 详情
        """
        app = self.get_app(_id)
        self.success(data=app.ifull)

    @authenticated
    def post(self, _id):
        """更新我的 App 属性
        """
        app = self.get_app(_id)
        body = self.get_body_json()
        params_count = len(body)
        if "name" in body:
            name = body.pop("name")
            if self.db.query(App).filter(and_(
                    App.user_id == self.current_user.id,
                    App.name == name,  # 名称不能相同
                    App.id != app.id,  # 不是当前 App
            )).first():
                self.fail("name-exist")
                return
            app.name = name
        if "app_secret" in body:
            app.set_secret(body.pop("app_secret"))
        if "summary" in body:
            app.summary = body.pop("summary")
        if "description" in body:
            app.description = body.pop("description")
        if "is_active" in body:
            is_active = body.pop("is_active")
            if is_active in [False, True]:
                app.is_active = is_active
        if params_count > 0:
            app.updated = datetime.datetime.utcnow()
            self.db.commit()

        self.success()

    @authenticated
    def delete(self, _id):
        """删除我的 App
        """
        app = self.get_app(_id)
        self._remove_app(app)
        self.success()

    def _remove_app(self, app):
        self.current_user.apps.remove(app)

        # 删除自身
        self.db.delete(app)

        self.db.commit()
