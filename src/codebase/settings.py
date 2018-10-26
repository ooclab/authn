DEBUG = True
SYNC_DATABASE = True

SECRET_KEY = "IpVDzxWOPQP9xxONJYdUHK1PNcyt4182Zulua6xfWkvZgp"

# http://docs.sqlalchemy.org/en/latest/core/engines.html
DB_URI = "sqlite://"

PAGE_SIZE = 10

# 用户初始化
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ooclab"

# 用户 session 默认有效期为2天
USER_SESSION_AGE = 2 * 24 * 3600
# 客户端 session 默认有效期为30天
CLIENT_SESSION_AGE = 30 * 24 * 3600
# 客户端最大并行会话数量（通过 refresh_token 仅能限制允许刷新）
MAX_SESSION = 5

# APP
MAX_APP = 5

# access_token 默认有效期为2小时
ACCESS_TOKEN_AGE = 2 * 3600

# Authorization server（AS）
# [OpenID Connect 认证](https://help.aliyun.com/document_detail/48019.html)
# https://plus.ooclab.com/note/article/1357
# openssl genpkey -algorithm RSA -out prikey.pem -pkeyopt rsa_keygen_bits:2048
AS_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEwAIBADANBgkqhkiG9w0BAQEFAASCBKowggSmAgEAAoIBAQDxKNwSwBYHN9aQ
XCbXbjBkZCHPe6euxJrSuktkkSw1405KQYFvRLmvL7IuQbfIgvxGw9lrXpYR6KBH
MpFV3EJO8yc4HXhKjyQuuX1GW/88u1i5RACQjz5Etpwv0nNumyzEZ5PDCBvu1sgG
Gyl2XZe09MKt4zLN3AbIAG2dB6yVc9k7U5q+Hnbdu0dtI19w0STpZRCJpNkRku8z
pRxWXA0XamBHewhv1y9AwaR097HS4ljPy78ciZn6WS5LHXKNuRlgLVxd+WEqW8mI
wuLPT2aB4OIVfDpsbLFpG5bjzm88dejj+nZoPz3rwwTp+BfqkXWBhwn64BbSr5+6
Lh1NrNP/AgMBAAECggEBAO8Q2lmcIjo1mHazY63chgx/VyUgKDKQpAqSs3qWj4U8
OLhUB8QOFSUd2z0P2OjlMMHWFQrjUVGfkoQCFSFQoEszsIVocX84N146c330ZSoH
bwT57LVhyxDDFkIyFkxneBGbvFdzCn3SXafv9UJptaKloPhQamS44eASzJcGrIfZ
y5yqRAzoW8NRcpJIfphpwLsOPa2Lllp5TRjFmxGYZUMkzcTnI1RdqrdQ1+hvc/Xf
GpEFDh858pyypDZkQZZQjEpFF42rWC4jwUX64rnHjJ71LNPrwodLjnlDqc0E4YO3
fXBZmN8TDMYBo5pvHxvoCqIdlRSVDMqZLBCz2H1tywECgYEA/X+HKPt8Ms2A+WoH
RQtoIfyOjHtLsAn/k+ZqMcpWWzuCaCv0V3QKStPjeGtD+OrR17YOJrP6KHwpmif8
UNYBne8K09L6S5/3R5l0nqH+Btcq1y0Fqd1LHKVm9866yoLviTbk0hAkG9PAbBKZ
coODo6r7ZafiDAkYZCLOJlkYJU8CgYEA84oobSEvpRPNBabUSi6G5BOVgxhuQ/VD
EZedQORmUWJQHkaBJHB2vjMSYKUlQGdf6NfLqHfpb1K55iABvBOhR5M80QkT7fEM
VuYVpdlc0qtdsxyRlhBKENIif88BferSv/rrTS4J3/Q0vn7XgAEMWAYc95GGqIfv
mPy46yERGlECgYEAuo/ogRjURu9HREfsIbxLXvfoUStMgLpbBhZFgW9QLsSVLOVs
ZhBYosleV3laBQ+McBzkPUeni7QVSgazgyp89ia+6TYUTyPjcSZW1YiS06X3OXVA
/cqHRQXVyfqzLec/MtTbgl2utWwZ6W+mzshLUWC8tAviKMlo0glrfn2Db7ECgYEA
4pv6k9jeUXdEPW8Hd+MlJtJGO46fA2MSviraawhbYHzfWdx2zCZNhxtUjVL9f5jw
+GLboO266xgJ3GSJ2KxXVJdfbo5I2g2CUtWS7Rh9M5W7AS+jFAQiNtagvVYr6DN5
WKOtEMq264l7DopOEVBoYPuHNqFVsDmUq0D0++xv0pECgYEAkNtCab4H7Qep0/ia
80V7SklBce/wN+EEJhTTcL4Z83PERWBfJbcs+Xki9s7Lwyz1bHg+HwDDpUXVAAyw
L5pg3N0vTpTwgaPeTAAAirS5ygCeiOm7EM7sPV6WdKe50i9I4QyZbwSAlU0o3bvD
IUFRDtJ5hxH90q1xR9uWdYeSNAI=
-----END PRIVATE KEY-----"""
# openssl rsa -pubout -in prikey.pem -out pubkey.pem
AS_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8SjcEsAWBzfWkFwm124w
ZGQhz3unrsSa0rpLZJEsNeNOSkGBb0S5ry+yLkG3yIL8RsPZa16WEeigRzKRVdxC
TvMnOB14So8kLrl9Rlv/PLtYuUQAkI8+RLacL9JzbpssxGeTwwgb7tbIBhspdl2X
tPTCreMyzdwGyABtnQeslXPZO1Oavh523btHbSNfcNEk6WUQiaTZEZLvM6UcVlwN
F2pgR3sIb9cvQMGkdPex0uJYz8u/HImZ+lkuSx1yjbkZYC1cXflhKlvJiMLiz09m
geDiFXw6bGyxaRuW485vPHXo4/p2aD8968ME6fgX6pF1gYcJ+uAW0q+fui4dTazT
/wIDAQAB
-----END PUBLIC KEY-----"""
# uuidgen
AS_KEY_ID = "8307402B-4DEC-41EF-B77B-C90FC5FD77E7"

JWT_ALGORITHM = "RS256"
