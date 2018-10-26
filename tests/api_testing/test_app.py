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
                api_secret="secret"
            )
            self.db.add(app)
        user = User(username="username", password="password")
        self.db.add(user)
        self.db.add(App(
            user=user,
            name="anotherapp",
            api_secret="secret"
        ))
        self.db.commit()
        self.assertEqual(self.db.query(App).count(), app_total+1)

        resp = self.api_get("/app")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        self.assertEqual(len(body["data"]), app_total)
        self.assertEqual(
            sorted([item["name"] for item in body["data"]]),
            sorted(["testapp"+str(i) for i in range(app_total)])
        )


class AppCreate(_Base):
    """POST /app - 创建 App
    """

    def test_name_exist(self):
        """App 名称已经存在
        """
        app = App(user=self.current_user, name="fortest", api_secret="secret")
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
        api_secret = "secret"
        resp = self.api_post("/app", body={
            "name": name,
            "api_secret": api_secret,
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
        self.assertEqual(app.validate_secret(api_secret), True)

    def test_create_full_success(self):
        """使用所有参数创建 App
        """
        user_pk_id = self.current_user.id
        request_body = {
            "name": "fortest",
            "api_secret": "secret",
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
        self.assertEqual(app.validate_secret(request_body["api_secret"]), True)
        self.assertEqual(request_body["summary"], app.summary)
        self.assertEqual(request_body["description"], app.description)
        self.assertEqual(request_body["is_active"], app.is_active)
