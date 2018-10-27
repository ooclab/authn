import uuid

from sqlalchemy import and_

from codebase.models import User, App
from codebase.utils.swaggerui import api

from .base import (
    BaseTestCase,
    validate_default_error,
    get_body_json
)


class _Base(BaseTestCase):

    rs = api.spec.resources["app"]


class AppList(_Base):
    """GET /app - 查看我所有的 App
    """

    def test_empty_apps(self):
        """无 App
        """
        resp = self.api_get("/app")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        self.assertEqual(len(body["data"]), 0)

    def test_many_apps(self):
        """有 App
        """

        app_total = 12
        for i in range(app_total):
            app = App(
                user=self.current_user,
                name="testapp" + str(i),
                app_secret="secret"
            )
            self.db.add(app)
        user = User(username="username", password="password")
        self.db.add(user)
        self.db.add(App(
            user=user,
            name="anotherapp",
            app_secret="secret"
        ))
        self.db.commit()
        self.assertEqual(self.db.query(App).count(), app_total + 1)

        resp = self.api_get("/app")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        self.assertEqual(len(body["data"]), app_total)
        self.assertEqual(
            sorted([item["name"] for item in body["data"]]),
            sorted(["testapp" + str(i) for i in range(app_total)])
        )


class AppCreate(_Base):
    """POST /app - 创建 App
    """

    def test_name_exist(self):
        """App 名称已经存在
        """
        app = App(user=self.current_user, name="fortest", app_secret="secret")
        self.db.add(app)
        self.db.commit()

        resp = self.api_post("/app", body={"name": app.name})
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "name-exist")

    def test_create_success(self):
        """创建成功
        """
        user_pk_id = self.current_user.id
        name = "for-ceate-test"
        app_secret = "secret"
        resp = self.api_post("/app", body={
            "name": name,
            "app_secret": app_secret,
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.post_app.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        app = self.db.query(App).filter(and_(
            App.user_id == user_pk_id,
            App.name == name,
        )).one()
        self.assertEqual(app.validate_secret(app_secret), True)

    def test_create_full_success(self):
        """使用所有参数创建 App
        """
        user_pk_id = self.current_user.id
        request_body = {
            "name": "fortest",
            "app_secret": "secret",
            "summary": "my first app",
            "description": "nothing to say",
            "is_active": False,
        }
        resp = self.api_post("/app", body=request_body)
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.post_app.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        app = self.db.query(App).filter(and_(
            App.user_id == user_pk_id,
            App.name == request_body["name"],
        )).one()
        self.assertEqual(app.validate_secret(request_body["app_secret"]), True)
        self.assertEqual(request_body["summary"], app.summary)
        self.assertEqual(request_body["description"], app.description)
        self.assertEqual(request_body["is_active"], app.is_active)


class AppView(_Base):
    """GET /app/{id} - 查看我的 App
    """

    def test_not_found(self):
        """App 不存在
        """

        app_id = str(uuid.uuid4())
        resp = self.api_get(f"/app/{app_id}")
        self.validate_not_found(resp)

    def test_not_my_app(self):
        """不是我的 App
        """
        user = User(username="username", password="password")
        self.db.add(user)
        self.db.commit()
        app = App(user=user, name="app", app_secret="secret")
        self.db.add(app)
        self.db.commit()

        resp = self.api_get(f"/app/{app.app_id}")
        self.validate_not_found(resp)

    def test_view_success(self):
        """查看成功
        """
        app = App(
            user=self.current_user,
            name="app",
            app_secret="secret",
            summary="summary",
            description="description"
        )
        self.db.add(app)
        self.db.commit()

        resp = self.api_get(f"/app/{app.app_id}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.get_app_id.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        data = body["data"]
        self.assertEqual(data["app_id"], str(app.app_id))
        self.assertEqual(data["name"], app.name)
        self.assertEqual(data["summary"], app.summary)
        self.assertEqual(data["description"], app.description)
        self.assertEqual(data["is_active"], app.is_active)


class AppUpdate(_Base):
    """POST /app/{id} - 更新我的 App
    """

    def test_not_found(self):
        """App 不存在
        """

        app_id = str(uuid.uuid4())
        resp = self.api_post(f"/app/{app_id}")
        self.validate_not_found(resp)

    def test_not_my_app(self):
        """不是我的 App
        """
        user = User(username="username", password="password")
        self.db.add(user)
        self.db.commit()
        app = App(user=user, name="app", app_secret="secret")
        self.db.add(app)
        self.db.commit()

        resp = self.api_post(f"/app/{app.app_id}")
        self.validate_not_found(resp)

    def test_update_success(self):
        """更新成功
        """
        app = App(user=self.current_user, name="app", app_secret="secret")
        self.db.add(app)
        self.db.commit()
        app_id = str(app.app_id)
        app_secret = "secret:new"
        request_body = {
            "name": app.name + ":new",
            "app_secret": app_secret,
            "summary": "add summary",
            "description": "add description",
            "is_active": False,
        }
        self.assertEqual(app.is_active, True)

        resp = self.api_post(f"/app/{app_id}", body=request_body)
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        del app
        app = self.db.query(App).filter_by(app_id=app_id).one()
        self.assertEqual(app.validate_secret(app_secret), True)
        self.assertEqual(app.name, request_body["name"])
        self.assertEqual(app.summary, request_body["summary"])
        self.assertEqual(app.description, request_body["description"])
        self.assertEqual(app.is_active, request_body["is_active"])

    def test_name_exist(self):
        """App 名称存在
        """
        app1 = App(user=self.current_user, name="app1", app_secret="secret")
        self.db.add(app1)
        app2 = App(user=self.current_user, name="app2", app_secret="secret")
        self.db.add(app2)
        self.db.commit()

        resp = self.api_post(f"/app/{app1.app_id}", body={"name": app2.name})
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "name-exist")


class AppDelete(_Base):
    """DELETE /app/{id} - 删除我的 App
    """

    def test_not_found(self):
        """App 不存在
        """

        app_id = str(uuid.uuid4())
        resp = self.api_delete(f"/app/{app_id}")
        self.validate_not_found(resp)

    def test_not_my_app(self):
        """不是我的 App
        """
        user = User(username="username", password="password")
        self.db.add(user)
        self.db.commit()
        app = App(user=user, name="app", app_secret="secret")
        self.db.add(app)
        self.db.commit()

        resp = self.api_delete(f"/app/{app.app_id}")
        self.validate_not_found(resp)

    def test_delete_success(self):
        """删除成功
        """
        user = User(username="username", password="password")
        self.db.add(user)
        app1 = App(user=user, name="app1", app_secret="secret")
        self.db.add(app1)
        app2 = App(user=self.current_user, name="app2", app_secret="secret")
        self.db.add(app2)
        self.db.commit()

        app2_id = str(app2.app_id)
        resp = self.api_delete(f"/app/{app2_id}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        del app2
        self.assertEqual(self.db.query(App).count(), 1)
        app = self.db.query(App).filter_by(app_id=app2_id).first()
        self.assertIsNone(app)
