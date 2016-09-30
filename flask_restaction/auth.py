import jwt
from datetime import datetime, timedelta
from flask import request, current_app, g
from werkzeug.http import dump_cookie


class TokenAuth:
    """Token based authorize and permission control"""

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
            headers.update(self.generate_headers(g.token))
        return rv, status, headers

    def get_role(self, f):
        """Decorater for register get_role_func"""
        self.get_role_func = f
        return f

    def generate_headers(self, token):
        """Generate auth headers"""
        headers = {}
        token = self.encode_token(token)
        if self.config["header"]:
            headers[self.config["header"]] = token
        if self.config["cookie"]:
            headers["Set-Cookie"] = dump_cookie(
                self.config["cookie"], token, httponly=True,
                max_age=self.config["expiration"]
            )
        return headers

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
        """Decode Authorization token, return None if token invalid"""
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
        """Encode Authorization token, return bytes token"""
        key = current_app.secret_key
        if key is None:
            raise ValueError("please set app.secret_key before generate token")
        return jwt.encode(token, key, algorithm=self.config["algorithm"])
