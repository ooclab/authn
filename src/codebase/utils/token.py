import datetime

import jwt
from eva.conf import settings

# [OpenID Connect 认证](https://help.aliyun.com/document_detail/48019.html)
# [JOSE 是什么？](https://plus.ooclab.com/note/article/1357)

# TODO: jwt 的签发和验证更规范


def gen_token(user, expired):
    # TODO: add Claims
    payload = {
        # 'aud': 'ooclab',
        "sub": "ooclab",
        "exp": expired,
        "iat": datetime.datetime.utcnow(),
        "iss": "ooclab",
    }
    payload.update({"uid": str(user.uuid)})
    tok = jwt.encode(
        payload,
        settings.AS_PRIVATE_KEY,
        algorithm=settings.JWT_ALGORITHM,
        headers={"kid": settings.AS_KEY_ID},
    )
    if isinstance(tok, bytes):
        tok = tok.decode("utf8")
    return tok


def decode_token(tok):
    return jwt.decode(
        tok,
        settings.AS_PUBLIC_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
