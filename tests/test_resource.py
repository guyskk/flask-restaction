# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import
from flask import Flask, request, g, url_for
from flask_restaction import Api, Resource
import pytest
import json
import six
"""
blueprint.resource@action
resource@action
blueprint.resource
resource
"""


def loads(data):
    if six.PY3:
        data = data.decode("utf-8")
    return json.loads(data)


@pytest.fixture(scope="module")
def app():
    app = Flask(__name__)
    app.debug = True
    api = Api(app)

    class Hello(Resource):

        def get(self):
            return "hello"

        def get_error(self):
            raise ValueError("get_error")

        def post_login(self):
            return "login"

    @Hello.error_handler
    def error_handler(ex):
        return {"ok": "error_hander"}

    class File(Resource):

        def get(self):
            return "file"

        def get_error(self):
            raise ValueError("get_error")

        def post_login(self):
            return "login"

    api.add_resource(Hello)
    # name can't be unicode on py2
    api.add_resource(File, name=str("upload"))

    return app


def test_hello(app):

    with app.test_request_context('/hello/login'):
        assert request.endpoint == 'hello@login'

    with app.test_request_context('/hello'):
        assert url_for("hello") == '/hello'
        assert url_for("hello@login") == '/hello/login'
        assert request.endpoint == 'hello'

    with app.test_client() as c:
        assert b'hello' == c.get('/hello').data
        assert b"login" == c.post('/hello/login').data
        assert 2 == c.get('/hello/error').status_code // 100
        assert b"ok"in c.get('/hello/error').data
        assert b"error_hander" in c.get('/hello/error').data


def test_unimplament_action(app):
    with app.test_client() as c:
        assert 404 == c.get("/unimplament_action").status_code
        assert 404 == c.post("/upload").status_code


def test_file(app):

    with app.test_request_context('/upload'):
        assert url_for("upload") == '/upload'
        assert url_for("upload@login") == '/upload/login'
        assert request.endpoint == 'upload'

    with app.test_request_context('/upload/login'):
        assert request.endpoint == 'upload@login'

    with app.test_client() as c:
        assert b'file' == c.get('/upload').data
        assert b"login" == c.post('/upload/login').data

    with app.test_client() as c:
        with pytest.raises(ValueError):
            try:
                c.get('/upload/error')
            except ValueError as ex:
                assert str(ex) == "get_error"
                raise


def test_user_role():
    class Hello(Resource):

        def get(self):
            return "hello"

        def post_login(self):
            me = {"id": 123}
            return "login", 200, api.gen_auth_header(me)

    def user_role(uid, user):
        return "role_%s" % uid
    app = Flask(__name__)
    app.debug = True
    api = Api(app, fn_user_role=user_role)
    api.add_resource(Hello)

    with app.test_client() as c:
        rv = c.post("/hello/login")
        assert b"login" in rv.data
        assert api.auth_header in rv.headers
        auth = {api.auth_header: rv.headers[api.auth_header]}
        rv2 = c.get("/hello", headers=auth)
        assert str(g.me["id"]) == "123"
        # if permission file not exists, user_role will not be called
        # assert g.me["role"] == "role_123"
        assert g.me["role"] == None


def test_request_content_type():
    class Hello(Resource):
        schema_inputs = {
            "post": {
                "name": {
                    "validate": "str"
                }
            }
        }

        def post(self, name):
            return {"hello": name}

    app = Flask(__name__)
    app.debug = True
    api = Api(app)
    api.add_resource(Hello)
    with app.test_client() as c:
        headers = {"Content-Type": "application/json"}
        assert 200 == c.post("/hello", headers=headers,
                             data='{"name": "hahah"}').status_code
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        assert 200 == c.post("/hello", headers=headers,
                             data='{"name": "hahah"}').status_code


def test_return_inner_custom_type():
    class User(object):

        def __init__(self, name):
            self.name = name

    class Hello(Resource):
        sche = {
            "name": {
                "validate": "str"
            }
        }
        schema_outputs = {
            "get": sche,
            "get_list": [sche],
            "get_dict": {
                "user": sche
            },
        }
        output_types = [User]

        def get(self):
            return User("kk")

        def get_list(self):
            return [User("kk")] * 10

        def get_dict(self):
            return {"user": User("kk")}
    app = Flask(__name__)
    app.debug = True
    api = Api(app)
    api.add_resource(Hello)
    with app.test_client() as c:
        assert 200 == c.get("/hello").status_code
        assert 200 == c.get("/hello/list").status_code
        assert 200 == c.get("/hello/dict").status_code
        user = loads(c.get("/hello").data)
        assert user == {
            "name": "kk"
        }
        userlist = loads(c.get("/hello/list").data)
        assert userlist == [{
            "name": "kk"
        }] * 10
        dd = loads(c.get("/hello/dict").data)
        assert dd["user"] == {
            "name": "kk"
        }
