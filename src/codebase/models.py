# pylint: disable=R0902,R0913,W0613,R0903

import datetime
import uuid
import string

from sqlalchemy_utils import UUIDType
from eva.conf import settings
from eva.utils.time_ import utc_rfc3339_string
from sqlalchemy import (
    event,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Sequence,
    String,
    Text,
    Boolean
)
from sqlalchemy.orm import relationship

from codebase.utils.sqlalchemy import ORMBase, dbc
from codebase.utils.enc import check_password, encrypt_password
from codebase.utils.random_ import randomstring


class User(ORMBase):

    __tablename__ = "authn_user"

    id = Column(Integer, Sequence("authn_user_id_seq"), primary_key=True)

    uuid = Column(UUIDType(), default=uuid.uuid4, unique=True)
    username = Column(String(64), nullable=False, unique=True)
    password = Column(String(512))

    is_active = Column(Boolean, default=True)  # 账户禁用与否

    created = Column(DateTime(), default=datetime.datetime.utcnow)
    updated = Column(DateTime(), default=datetime.datetime.utcnow)

    def __init__(self, username, password=None):
        self.username = username
        if password:
            self.password = encrypt_password(password)

    def validate_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        return check_password(raw_password, self.password)

    def set_password(self, raw_password):
        self.password = encrypt_password(raw_password)

    @property
    def ifull(self):
        return {
            "id": str(self.uuid),
            "username": self.username,
            "is_active": self.is_active,
            "updated": utc_rfc3339_string(self.updated),
            "created": utc_rfc3339_string(self.created),
        }


class App(ORMBase):
    """
    App 属于 User, 验证成功后，与所属的 User 有同样的权限

    TODO:
    1. 用户需要拥有多个不同权限的 App
    """

    __tablename__ = "authn_app"

    id = Column(Integer, Sequence("authn_app_id_seq"), primary_key=True)

    user_id = Column(Integer, ForeignKey("authn_user.id"))  # 创建用户 ID
    user = relationship("User", backref="apps")

    app_id = Column(UUIDType(), default=uuid.uuid4, unique=True)
    app_secret = Column(String(256), nullable=False)

    # 方便用户自行管理的属性
    name = Column(String(128), unique=True)
    summary = Column(String(1024))
    description = Column(Text)

    is_active = Column(Boolean, default=True)  # 是否启用

    created = Column(DateTime(), default=datetime.datetime.utcnow)
    updated = Column(DateTime(), default=datetime.datetime.utcnow)

    def __init__(
            self, user, name, app_secret,
            summary=None, description=None, is_active=None):
        self.user_id = user.id
        self.name = name
        self.app_secret = encrypt_password(app_secret)
        if summary:
            self.summary = summary
        if description:
            self.description = description
        if is_active in [False, True]:
            self.is_active = is_active

    def set_secret(self, raw_secret):
        self.app_secret = encrypt_password(raw_secret)

    def validate_secret(self, raw_app_secret):
        return check_password(raw_app_secret, self.app_secret)

    @property
    def isimple(self):
        return {
            "app_id": str(self.app_id),
            "is_active": self.is_active,
            "name": self.name,
            "summary": self.summary,
        }

    @property
    def ifull(self):
        return {
            "app_id": str(self.app_id),
            "is_active": self.is_active,
            "name": self.name,
            "summary": self.summary,
            "description": self.description,
            "updated": utc_rfc3339_string(self.updated),
            "created": utc_rfc3339_string(self.created),
        }


class UserSession(ORMBase):
    """
    UserSession 保存 refresh_token
    """

    __tablename__ = "authn_user_session"

    id = Column(Integer, Sequence("authn_user_session_id_seq"), primary_key=True)
    refresh_token = Column(String(128), nullable=False, unique=True)

    user_id = Column(Integer, ForeignKey("authn_user.id"))
    user = relationship("User", backref="sessions")

    created = Column(DateTime(), default=datetime.datetime.utcnow)
    expires_in = Column(DateTime())

    def __init__(self, user):
        self.user = user
        self.refresh_token = randomstring(
            128, scope=string.ascii_letters + string.digits)
        self.expires_in = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=int(settings.USER_SESSION_AGE)
        )

    @property
    def is_expired(self):
        return datetime.datetime.utcnow() > self.expires_in


class AppSession(ORMBase):
    """
    AppSession 保存 refresh_token
    """

    __tablename__ = "authn_app_session"

    id = Column(Integer, Sequence("authn_app_session_id_seq"), primary_key=True)
    refresh_token = Column(String(128), nullable=False, unique=True)

    app_id = Column(Integer, ForeignKey("authn_app.id"))
    app = relationship("App", backref="sessions")

    created = Column(DateTime(), default=datetime.datetime.utcnow)
    expires_in = Column(DateTime())

    def __init__(self, app):
        self.app = app
        self.refresh_token = randomstring(
            128, scope=string.ascii_letters + string.digits)
        self.expires_in = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=int(settings.USER_SESSION_AGE)
        )

    @property
    def is_expired(self):
        return datetime.datetime.utcnow() > self.expires_in


# User 表创建后，创建默认用户
@event.listens_for(User.__table__, 'after_create')
def insert_initial_users(*args, **kwargs):
    db = dbc.session()
    # !important! 用户是否有管理员权限，需要在 authz 服务中增加 admin 角色
    db.add(User(username=settings.ADMIN_USERNAME,
                password=settings.ADMIN_PASSWORD))
    db.commit()
