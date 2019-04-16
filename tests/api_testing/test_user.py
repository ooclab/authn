import uuid

from codebase.models import User, App
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

        spec = self.rs.post_user.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        user = self.db.query(User).filter_by(username=username).one()
        self.assertEqual(user.validate_password(password), True)


class UserViewTestCase(_Base):
    """GET /user/{id} - 查看用户详情
    """

    def test_not_found(self):
        """用户不存在
        """

        user_id = str(uuid.uuid4())
        resp = self.api_get(f"/user/{user_id}")
        self.validate_not_found(resp)

    def test_view_success(self):
        """查看成功
        """
        resp = self.api_get(f"/user/{self.current_user.uuid}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.get_user_id.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        data = body["data"]
        self.assertEqual(data["username"], self.current_username)


class UserUpdateTestCase(_Base):
    """POST /user/{id} - 更新用户属性
    """

    def test_not_found(self):
        """用户不存在
        """

        user_id = str(uuid.uuid4())
        resp = self.api_post(f"/user/{user_id}")
        self.validate_not_found(resp)

    def test_update_success(self):
        """更新成功
        """
        username = "fortest"
        password = "password"
        user = User(username=username, password=password)
        self.db.add(user)
        self.db.commit()

        resp = self.api_post(f"/user/{user.uuid}", body={
            "username": username + ":new",
            "password": password + ":new",
        })
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        del user
        user = self.db.query(User).filter_by(username=username + ":new").one()
        self.assertEqual(user.validate_password(password + ":new"), True)

    def test_username_exist(self):
        """用户名存在
        """
        username = "fortest"
        user = User(username=username, password="password")
        self.db.add(user)
        self.db.commit()
        self.assertEqual(user.is_active, True)

        resp = self.api_post(f"/user/{user.uuid}", body={
            "username": self.current_username})
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)
        self.assertEqual(body["status"], "username-exist")

    def test_is_active_false(self):
        """禁止用户
        """
        username = "fortest"
        user = User(username=username, password="password")
        self.db.add(user)
        self.db.commit()
        self.assertEqual(user.is_active, True)

        resp = self.api_post(f"/user/{user.uuid}", body={"is_active": False})
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        del user
        user = self.db.query(User).filter_by(username=username).one()
        self.assertEqual(user.is_active, False)


class UserDeleteTestCase(_Base):
    """DELETE /user/{id} - 删除用户
    """

    def test_not_found(self):
        """用户不存在
        """

        user_id = str(uuid.uuid4())
        resp = self.api_delete(f"/user/{user_id}")
        self.validate_not_found(resp)

    def test_delete_success(self):
        """删除成功
        """
        username = "fortest"
        password = "password"
        user = User(username=username, password=password)
        self.db.add(user)
        self.db.commit()

        app_total = 12
        for i in range(app_total):
            app = App(
                user=user,
                name="testapp" + str(i),
                app_secret="secret"
            )
            self.db.add(app)
        self.db.add(App(
            user=self.current_user,
            name="anotherapp",
            app_secret="secret"
        ))
        self.db.commit()
        self.assertEqual(self.db.query(App).count(), app_total+1)

        resp = self.api_delete(f"/user/{user.uuid}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        del user
        self.assertEqual(self.db.query(App).count(), 1)
        user = self.db.query(User).filter_by(username=username).first()
        self.assertIsNone(user)


class UserByNameTestCase(_Base):
    """GET /user/by_name/{username} - 指定用户名，查看用户详情
    """

    def test_not_found(self):
        """用户不存在
        """

        resp = self.api_get("/user/by_name/not_exist")
        self.validate_not_found(resp)

    def test_view_success(self):
        """查看成功
        """
        resp = self.api_get(f"/user/by_name/{self.current_user.username}")
        body = get_body_json(resp)
        self.assertEqual(resp.code, 200)
        self.validate_default_success(body)

        spec = self.rs.get_user_by_name_username.op_spec["responses"]["200"]["schema"]
        api.validate_object(spec, body)

        data = body["data"]
        self.assertEqual(data["username"], self.current_username)
