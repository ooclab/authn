# pylint: disable=W0223,W0221,broad-except

from sqlalchemy import and_

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
            api_secret=body["api_secret"],
            summary=body.get("summary"),
            description=body.get("description"),
            is_active=body.get("is_active")
        )
        self.db.add(app)
        self.db.commit()
        self.success(id=str(app.uuid))
