import json
import jwt
from flask import Flask, g
from flask_restaction import Api, TokenAuth
from freezegun import freeze_time
from helper import resp_json

AUTH_HEADER = "Authorization"


def create_app(tmpdir, refresh=True, cookie=None):
    class Hello:

        def get(self):
            """
            Get Name

            $output:
                name?str&optional: Your name
            """
            return {"name": g.token["name"]}

        def post(self, name):
            """
            Generate Token

            $input:
                name?str: Your name
            """
            if name == "admin":
                role = "admin"
            else:
                role = "normal"
            g.token = {"role": role, "name": name}
            return "OK"

    metafile = tmpdir.join("meta.json")
    json.dump({
        "$desc": "test",
        "$auth": {
            "refresh": refresh,
            "cookie": cookie
        },
        "$roles": {
            "admin": {
                "hello": ["get", "post"]
            },
            "guest": {
                "hello": ["post"]
            }
        }
    }, metafile.open("w"))

    app = Flask(__name__)
    app.secret_key = "secret_key"
    api = Api(app, metafile=metafile.strpath)

    auth = TokenAuth(api)

    @auth.get_role
    def get_role(token):
        if token:
            return token["role"]
        else:
            return "guest"

    api.add_resource(Hello)
    return app


def test_auth(tmpdir):
    app = create_app(tmpdir)
    with app.test_client() as c:
        resp = c.get("/hello")
        assert resp.status_code == 403
        assert resp_json(resp)["error"] == "PermissionDeny"
        assert "guest" in resp_json(resp)["message"]

        resp = c.post("/hello", data={"name": "abc"})
        assert resp.status_code == 200
        headers = {AUTH_HEADER: resp.headers[AUTH_HEADER]}
        resp = c.get("/hello", headers=headers)
        assert resp.status_code == 403
        assert resp_json(resp)["error"] == "PermissionDeny"
        assert "normal" in resp_json(resp)["message"]

        resp = c.post("/hello", data={"name": "admin"})
        assert resp.status_code == 200
        headers = {AUTH_HEADER: resp.headers[AUTH_HEADER]}
        resp = c.get("/hello", headers=headers)
        assert resp.status_code == 200
        assert resp_json(resp) == {"name": "admin"}


def test_no_secret_key():
    app = Flask(__name__)
    api = Api(app)
    auth = TokenAuth(api)
    with app.test_request_context("/"):
        token = jwt.encode({"user_id": 1}, "")
        assert auth.decode_token(token) is None


def test_expiration(tmpdir):
    app = create_app(tmpdir)
    with app.test_client() as c:
        with freeze_time("2016-09-15T15:00:00Z"):
            resp = c.post("/hello", data={"name": "admin"})
            assert resp.status_code == 200
        headers = {AUTH_HEADER: resp.headers[AUTH_HEADER]}
        with freeze_time("2016-09-15T15:29:59Z"):
            resp = c.get("/hello", headers=headers)
            assert resp.status_code == 200
            # not create new token
            assert AUTH_HEADER not in resp.headers
        with freeze_time("2016-09-15T15:30:01Z"):
            resp = c.get("/hello", headers=headers)
            assert resp.status_code == 200
            # create new token, can reuse 60min from now
            assert AUTH_HEADER in resp.headers
        with freeze_time("2016-09-15T15:59:59Z"):
            resp = c.get("/hello", headers=headers)
            assert resp.status_code == 200
            # create new token, can reuse 60min from now
            assert AUTH_HEADER in resp.headers
        new_headers = {AUTH_HEADER: resp.headers[AUTH_HEADER]}
        with freeze_time("2016-09-15T16:00:01Z"):
            # token invalid
            resp = c.get("/hello", headers=headers)
            assert resp.status_code == 403
            # use new token
            resp = c.get("/hello", headers=new_headers)
            assert resp.status_code == 200
        with freeze_time("2016-09-15T16:59:58Z"):
            # use new token
            resp = c.get("/hello", headers=new_headers)
            assert resp.status_code == 200
        with freeze_time("2016-09-15T17:00:01Z"):
            # token invalid
            resp = c.get("/hello", headers=new_headers)
            assert resp.status_code == 403


def test_disable_refresh(tmpdir):
    app = create_app(tmpdir, refresh=False)
    with app.test_client() as c:
        with freeze_time("2016-09-15T15:00:00Z"):
            resp = c.post("/hello", data={"name": "admin"})
            assert resp.status_code == 200
        headers = {AUTH_HEADER: resp.headers[AUTH_HEADER]}
        with freeze_time("2016-09-15T15:30:01Z"):
            resp = c.get("/hello", headers=headers)
            assert resp.status_code == 200
            # not create new token
            assert AUTH_HEADER not in resp.headers
        with freeze_time("2016-09-15T15:59:59Z"):
            resp = c.get("/hello", headers=headers)
            assert resp.status_code == 200
            # not create new token
            assert AUTH_HEADER not in resp.headers
        with freeze_time("2016-09-15T16:00:01Z"):
            # token invalid
            resp = c.get("/hello", headers=headers)
            assert resp.status_code == 403


def test_enable_cookie(tmpdir):
    cookie_name = "Authorization"
    app = create_app(tmpdir, cookie=cookie_name)
    with app.test_client() as c:
        with freeze_time("2016-09-15T15:00:00Z"):
            resp = c.post("/hello", data={"name": "admin"})
            assert resp.status_code == 200
            assert "Set-Cookie" in resp.headers
        with freeze_time("2016-09-15T15:29:59Z"):
            resp = c.get("/hello")
            assert resp.status_code == 200
            assert "Set-Cookie" not in resp.headers
        with freeze_time("2016-09-15T16:00:01Z"):
            resp = c.get("/hello")
            # token invalid
            assert resp.status_code == 403
        with freeze_time("2016-09-15T15:59:59Z"):
            resp = c.get("/hello")
            assert resp.status_code == 200
