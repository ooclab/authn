# pylint: disable=R0903

import unittest

from codebase.utils.sqlalchemy import dbc


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ok '\033[92m\u2713\033[0m'
# \u21E8 输出 ⇨
# \u21B3 输出 ↳
# \u21E2 输出 ⇢
# \u2B91 输出 ⮑
# \u2937 输出 ⤷
# \u27F3 输出 ⟳
# \u2B51 输出 ⭑
# \u2713 输出 ✓


FIRST_ARROW = f"{Bcolors.OKGREEN}\u21E8{Bcolors.ENDC}"
SECOND_ARROW = f"{Bcolors.WARNING}\u21E2{Bcolors.ENDC}"


class BaseTestCase(unittest.TestCase):

    main_title = None

    def shortDescription(self):
        class_doc = self.__doc__
        doc = self._testMethodDoc
        first = class_doc.split("\n")[0].strip() if class_doc else None
        second = doc.split("\n")[0].strip() if doc else None
        if not self.main_title:
            self.__class__.main_title = True
            return (f"\n{FIRST_ARROW} {Bcolors.BOLD}{first}{Bcolors.ENDC}\n"
                    f"  {SECOND_ARROW} {second}")
        return f"  {SECOND_ARROW} {second}"

    def setUp(self):
        # 每个 testcase 执行前都会执行
        super().setUp()
        dbc.create_all()

    def tearDown(self):
        # 每个 testcase 执行后都会执行
        super().tearDown()
        # dbc.remove()
        dbc.drop_all()

    @property
    def db(self):
        return dbc.session()
