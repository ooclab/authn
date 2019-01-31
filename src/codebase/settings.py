DEBUG = "false"
CORS = "false"
SYNC_DATABASE = "false"

SECRET_KEY = "IpVDzxWOPQP9xxONJYdUHK1PNcyt4182Zulua6xfWkvZgp"

# http://docs.sqlalchemy.org/en/latest/core/engines.html
DB_URI = "sqlite://"
DB_CONNECT_TIMEOUT = 10

PAGE_SIZE = 10

# 用户初始化
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ooclab"

# 用户 session 默认有效期为2天
USER_SESSION_AGE = 2 * 24 * 3600
# 客户端 session 默认有效期为365天
CLIENT_SESSION_AGE = 365 * 24 * 3600
# 客户端最大并行会话数量（通过 refresh_token 仅能限制允许刷新）
MAX_SESSION_PER_USER = 6

# APP
MAX_APP = 5

# User access_token 默认有效期为2小时
USER_ACCESS_TOKEN_AGE = 2 * 3600
# App access_token 默认有效期为30天
APP_ACCESS_TOKEN_AGE = 30 * 24 * 3600

# [OpenID Connect 认证](https://help.aliyun.com/document_detail/48019.html)
# https://plus.ooclab.com/note/article/1357
# openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048
# openssl rsa -pubout -in private_key.pem -out public_key.pem
TOKEN_KEY_PATH = "~/.authn/keys/"
# uuidgen
TOKEN_KEY_ID = "8307402B-4DEC-41EF-B77B-C90FC5FD77E7"
TOKEN_ALGORITHM = "RS256"
