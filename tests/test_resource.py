#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function

from flask import Flask, request, g, url_for
from flask_restaction import Api, Resource
import pytest
"""
blueprint.resource@action
resource@action
blueprint.resource
resource
"""


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.debug = True
    api = Api(app)

    class Hello(Resource):

        def get(self):
            return "hello"

        def get_error(self):
            raise ValueError("error")

        def post_login(self):
            return "login"

    api.add_resource(Hello)
    # name can't be unicode on py2
    api.add_resource(Hello, name=str("hi"))

    app.resource = Hello
    app.api = api
    return app


def test_url_for(app):
    with app.test_request_context('/hello'):
        assert request.endpoint == 'hello'
        assert url_for("hello") == '/hello'
    with app.test_request_context('/hello/login'):
        assert request.endpoint == 'hello@login'
        assert url_for("hello@login") == '/hello/login'
    with app.test_request_context('/hello/error'):
        assert request.endpoint == 'hello@error'
        assert url_for("hello@error") == '/hello/error'

    with app.test_request_context('/hi'):
        assert request.endpoint == 'hi'
        assert url_for("hi") == '/hi'
    with app.test_request_context('/hi/login'):
        assert request.endpoint == 'hi@login'
        assert url_for("hi@login") == '/hi/login'
    with app.test_request_context('/hi/error'):
        assert request.endpoint == 'hi@error'
        assert url_for("hi@error") == '/hi/error'


def test_error_handler(app):

    @app.resource.error_handler
    def error_handler(self, ex):
        assert isinstance(ex, ValueError)
        assert ex.args == ('error',)
        return "error_hander"
    with app.test_client() as c:
        assert 200 == c.get('/hello').status_code
        assert b'hello' == c.get('/hello').data

        assert 200 == c.post('/hello/login').status_code
        assert b"login" == c.post('/hello/login').data

        assert 200 == c.get('/hello/error').status_code
        assert b"error_hander" == c.get('/hello/error').data


def test_before_request(app):
    @app.resource.before_request
    def before_request(self):
        return 'before_request'

    with app.test_client() as c:
        assert 200 == c.get('/hello').status_code
        assert b'before_request' == c.get('/hello').data

        assert 200 == c.post('/hello/login').status_code
        assert b"before_request" == c.post('/hello/login').data

        assert 200 == c.get('/hello/error').status_code
        assert b"before_request" == c.get('/hello/error').data


def test_after_request(app):
    @app.resource.after_request
    def after_request(self, rv, code, headers):
        return 'after_request', 200, headers

    with app.test_client() as c:
        assert 200 == c.get('/hello').status_code
        assert b'after_request' == c.get('/hello').data

        assert 200 == c.post('/hello/login').status_code
        assert b"after_request" == c.post('/hello/login').data

        with pytest.raises(ValueError) as exinfo:
            c.get('/hello/error')
        assert exinfo.value.args == ('error',)


def test_unimplament_action(app):
    with app.test_client() as c:
        assert 404 == c.get("/unimplament").status_code
        assert 404 == c.get("/hello/login").status_code
        assert 405 == c.put("/hello/login").status_code
        assert 405 == c.delete("/hello/login").status_code


def test_request_content_type():
    class Hello(Resource):
        schema_inputs = {
            "post": {"name": "safestr"}
        }

        def post(self, name):
            return {"hello": name}

    app = Flask(__name__)
    app.debug = True
    api = Api(app)
    api.add_resource(Hello)
    with app.test_client() as c:
        headers = {"Content-Type": "application/json"}
        params = dict(headers=headers, data='{"name": "jsoner"}')
        assert 200 == c.post("/hello", **params).status_code
        headers["Content-Type"] = "application/json;charset=UTF-8"
        assert 200 == c.post("/hello", **params).status_code
