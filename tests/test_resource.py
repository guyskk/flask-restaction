# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import
from flask import Flask, request, url_for
from flask_restaction import Api, Resource
import pytest
import json
"""
blueprint.resource@action
resource@action
blueprint.resource
resource
"""


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
        assert url_for("file") == '/upload'
        assert url_for("file@login") == '/upload/login'
        assert request.endpoint == 'file'

    with app.test_request_context('/upload/login'):
        assert request.endpoint == 'file@login'

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
        assert str(request.me["id"]) == "123"
        assert request.me["role"] == "role_123"


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
