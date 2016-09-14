import jwt
from datetime import datetime, timedelta
from flask import request, current_app, g
from werkzeug.http import dump_cookie


class TokenAuth:
    """
    处理Token授权

    用法::

        # meta.json
        {
            "$auth": {
                "algorithm": "HS256",     # token签名算法
                "expiration": 3600,       # token存活时间，单位为秒
                "header": "Authorization" # 用于传递token的请求/响应头
                "cookie": null            # 用于传递token的cookie, 默认不用cookie
                "refresh": true           # 是否主动延长token过期时间
            }
        }

        # __init__.py
        auth = TokenAuth(api)
        @auth.get_role
        def get_role(self, token):
            if token:
                return token.get('role', 'guest')
            return 'guest'

        # user.py
        class User:
            def post_login(self, userid, password):
                # query user from database, check userid and password
                g.token={'userid': userid, 'role': role}
                return "OK"

    对安全性要求不同，授权相关的实现也会不同，这里的实现适用于对安全性要求不高的应用。

    当收到请求时，检测到token即将过期，会主动颁发一个新的token给客户端，
    这样能避免token过期导致中断用户正常使用的问题。

    但这样也导致token能够被无限被刷新，有一定的安全隐患。
    设置``"refresh": false``可以禁止主动颁发新的token给客户端。
    """

    def __init__(self, api):
        self.api = api
        self.config = api.meta["$auth"]
        self.get_role_func = None
        api.before_request(self.before_request)
        api.after_request(self.after_request)

    def before_request(self):
        token = None
        if token is None and self.config["header"]:
            token = request.headers.get(self.config["header"])
        if token is None and self.config["cookie"]:
            token = request.cookies.get(self.config["cookie"])
        if token:
            token = self.decode_token(token)
        g.token = token
        self.api.authorize(self.get_role_func(token))

    def after_request(self, rv, status, headers):
        exp = self.calculate_expiration(g.token)
        if exp:
            g.token["exp"] = exp
            if headers is None:
                headers = {}
            token = self.encode_token(g.token)
            if self.config["header"]:
                headers[self.config["header"]] = token
            if self.config["cookie"]:
                headers["Set-Cookie"] = dump_cookie(
                    self.config["cookie"], token, httponly=True,
                    max_age=self.config["expiration"]
                )
        return rv, status, headers

    def get_role(self, f):
        """Decorater for register get_role_func"""
        self.get_role_func = f
        return f

    def calculate_expiration(self, token):
        """Calculate token expiration

        return expiration if the token need to set expiration or refresh,
        otherwise return None.
        """
        if not token:
            return None
        now = datetime.utcnow()
        time_to_live = self.config["expiration"]
        if "exp" not in token:
            return now + timedelta(seconds=time_to_live)
        elif self.config["refresh"]:
            exp = datetime.fromtimestamp(token["exp"])
            # 0.5: reduce refresh frequent
            if exp - now < timedelta(seconds=0.5 * time_to_live):
                return now + timedelta(seconds=time_to_live)
        return None

    def decode_token(self, token):
        """Decode Authorization token"""
        key = current_app.secret_key
        if key is None:
            if current_app.debug:
                current_app.logger.debug("app.secret_key not set")
            return None
        try:
            return jwt.decode(
                token, key,
                algorithms=[self.config["algorithm"]],
                options={'require_exp': True}
            )
        except jwt.InvalidTokenError:
            return None

    def encode_token(self, token):
        """Encode Authorization token"""
        key = current_app.secret_key
        if key is None:
            raise ValueError("please set app.secret_key before generate token")
        return jwt.encode(token, key, algorithm=self.config["algorithm"])
