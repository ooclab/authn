from tornado.web import url

from codebase.controllers import (
    default,
    user
)


HANDLERS = [
    url(r"/_spec",
        default.SpecHandler),

    url(r"/_health",
        default.HealthHandler),

    # User

    url(r"/user",
        user.UserHandler),

    # url(r"/role/"
    #     r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
    #     role.SingleRoleHandler),
]
