from tornado.web import url

from codebase.controllers import (
    default,
    token,
    user,
    app
)


HANDLERS = [

    url(r"/",
        default.SpecHandler),

    url(r"/_health",
        default.HealthHandler),

    # Token

    url(r"/token",
        token.UserTokenHandler),

    url(r"/token/refresh",
        token.UserTokenRefreshHandler),

    url(r"/app_token",
        token.SingleAppTokenHandler),

    url(r"/app_token/refresh",
        token.SingleAppTokenRefreshHandler),

    url(r"/open_token",
        token.OpenTokenHandler),

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
