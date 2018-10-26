from tornado.web import url

from codebase.controllers import (
    default,
    token,
    user,
    app
)


HANDLERS = [

    url(r"/_spec",
        default.SpecHandler),

    url(r"/_health",
        default.HealthHandler),

    # Token

    url(r"/user/token",
        token.UserTokenHandler),

    url(r"/user/token/refresh",
        token.UserTokenRefreshHandler),

    url(r"/app/"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
        "/token",
        token.SingleAppTokenHandler),

    url(r"/app/"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
        "/token/refresh",
        token.SingleAppTokenRefreshHandler),

    # User

    url(r"/user",
        user.UserHandler),

    url(r"/user/"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        user.SingleUserHandler),

    # App

    url(r"/app",
        app.AppHandler),

    url(r"/app/"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        app.SingleAppHandler),

]
