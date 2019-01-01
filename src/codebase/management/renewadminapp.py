# pylint: disable=R0201

import logging

from sqlalchemy import and_
from eva.conf import settings
from eva.management.common import EvaManagementCommand

from codebase.models import User, App
from codebase.utils.sqlalchemy import dbc
from codebase.utils.random_ import randomstring


class Command(EvaManagementCommand):
    def __init__(self):
        super(Command, self).__init__()

        self.cmd = "renewadminapp"
        self.help = "创建管理员的 app"

    def run(self):
        db = dbc.session()
        admin = db.query(User).filter_by(
            username=settings.ADMIN_USERNAME).first()
        if not admin:
            logging.error(
                "can not find admin account (%s)", settings.ADMIN_USERNAME)
            return

        app_name = "adminapp"
        app_secret = randomstring(32)

        app = db.query(App).filter(
            and_(App.user_id == admin.id, App.name == app_name)).first()
        if app:
            app.set_secret(app_secret)
        else:
            app = App(user=admin, name=app_name, app_secret=app_secret)
            db.add(app)
            db.commit()

        print(f"Update admin app success:\n"
              f"username={admin.username}\n"
              f"user_id={admin.uuid}\n"
              f"app_id={app.app_id}\n"
              f"app_secret={app_secret}")
