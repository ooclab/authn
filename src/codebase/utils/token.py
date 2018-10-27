# pylint: disable=R0201,C0103

import os
import datetime
from pathlib import Path

import jwt
from eva.conf import settings

from .crypto import generate_keys
from .config import GlobalSetting

# [OpenID Connect 认证](https://help.aliyun.com/document_detail/48019.html)
# [JOSE 是什么？](https://plus.ooclab.com/note/article/1357)

# TODO: jwt 的签发和验证更规范


class Token:

    def __init__(self):
        self.private_key = GlobalSetting.get("TOKEN_PRIVATE_KEY")
        self.public_key = GlobalSetting.get("TOKEN_PUBLIC_KEY")
        if self.private_key is None or self.public_key is None:
            self.private_key, self.public_key = self.load_keys()
            GlobalSetting.set("TOKEN_PRIVATE_KEY", self.private_key)
            GlobalSetting.set("TOKEN_PUBLIC_KEY", self.public_key)

    def gen_token(self, user, expired):
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
            self.private_key,
            algorithm=settings.TOKEN_ALGORITHM,
            headers={"kid": settings.TOKEN_KEY_ID},
        )
        if isinstance(tok, bytes):
            tok = tok.decode("utf8")
        return tok

    def decode_token(self, tok):
        return jwt.decode(
            tok,
            self.public_key,
            algorithm=settings.TOKEN_ALGORITHM
        )

    def load_keys(self):
        """加载密钥对
        """
        dpath = self.get_keys_path()
        prikey_path = os.path.join(dpath, "private_key.pem")
        pubkey_path = os.path.join(dpath, "public_key.pem")
        if os.path.exists(prikey_path) and os.path.exists(pubkey_path):
            return open(prikey_path).read(), open(pubkey_path).read()

        # 创建新的密钥对
        prikey, pubkey = generate_keys()
        # save to file
        self._save_keys_to_file(prikey, pubkey)
        return prikey, pubkey

    def _save_keys_to_file(self, private_key, public_key):
        """保存密钥对到文件
        """
        dpath = self.get_keys_path()
        if not os.path.exists(dpath):
            Path(dpath).mkdir(parents=True, exist_ok=True)

        with open(os.path.join(dpath, "private_key.pem"), "wb") as f:
            f.write(private_key)
        with open(os.path.join(dpath, "public_key.pem"), "wb") as f:
            f.write(public_key)

    def get_keys_path(self):
        dpath = settings.TOKEN_KEY_PATH
        if dpath:
            return os.path.expanduser(dpath)

        if os.getuid() == 0:
            dpath = "/etc/authn/keys/"
        else:
            home = Path.home()
            if not home.exists():
                home.mkdir()
            dpath = os.path.join(home.as_posix(), ".authn/keys/")
        return dpath


gen_token = Token().gen_token
decode_token = Token().decode_token
