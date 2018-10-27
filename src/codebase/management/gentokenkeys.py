# pylint: disable=R0201

from eva.management.common import EvaManagementCommand

from codebase.utils.token import Token


class Command(EvaManagementCommand):
    def __init__(self):
        super(Command, self).__init__()

        self.cmd = "gentokenkeys"
        self.help = "确认token密钥对(如果不存在，则创建之)"

    def run(self):
        Token()
