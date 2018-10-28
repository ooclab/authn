# pylint: disable=R0201

import logging

from eva.conf import settings
from eva.management.common import EvaManagementCommand

from codebase.models import User, App
from codebase.utils.sqlalchemy import dbc
from codebase.utils.random_ import randomstring


class Command(EvaManagementCommand):
    def __init__(self):
        super(Command, self).__init__()

        self.cmd = "createadminapp"
        self.help = "创建管理员的 app"

    def run(self):
        db = dbc.session()
        admin = db.query(User).filter_by(
            username=settings.ADMIN_USERNAME).first()
        if not admin:
            logging.error(
                "can not find admin account (%s)", settings.ADMIN_USERNAME)
            return

        app_secret = randomstring(32)
        app = App(user=admin, name="createadminapp", app_secret=app_secret)
        db.add(app)
        db.commit()

        print(f"Create Admin App Success:\n"
              f"app_id={app.app_id}\n"
              f"app_secret={app_secret}")
