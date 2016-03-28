#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function

from flask import Flask, Blueprint, g, url_for, request
from flask_restaction import Api, Resource
import validater
import pytest
from flask_restaction.api import load_options


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

    api.add_resource(Hello)
    app.resource = Hello
    app.api = api
    return app


def test_parse_request():
    class Hello(Resource):

        def get(self):
            return "hello"

    app = Flask(__name__)
    app.debug = True
    api = Api(app)
    api.add_resource(Hello)

    with app.test_request_context('hello'):
        assert request.endpoint == "hello"
        assert url_for("hello") == "/hello"
    with app.test_client() as c:
        rv = c.get("hello")
        assert 200 == rv.status_code
        assert b"hello" in rv.data
        assert g.resource == "hello"
        assert g.action == "get"


def test_blueprint():
    class Hello(Resource):

        def get(self):
            return "hello"

    app = Flask(__name__)
    app.debug = True
    bp = Blueprint("blueprint", __name__)
    api = Api(app, blueprint=bp)
    api.add_resource(Hello)
    app.register_blueprint(bp, url_prefix="/api")

    with app.test_request_context('/api/hello'):
        assert request.endpoint == "blueprint.hello"
        assert url_for("blueprint.hello") == "/api/hello"
    with app.test_client() as c:
        rv = c.get("/api/hello")
        assert 200 == rv.status_code
        assert b"hello" == rv.data
        assert g.resource == "hello"
        assert g.action == "get"


def test_parse_schema():
    hello = {"hello": "safestr&required"}
    sche_inputs = {
        "get": {"name": "name&default='world'"},
        "post_login": {
            "name": "name&default='world'",
            "password": "password&required"
        }
    }
    sche_outputs = {
        "get": hello,
        "post_login": hello
    }

    class Hello(Resource):

        schema_inputs = sche_inputs
        schema_outputs = sche_outputs
        output_types = [Flask]

        def get(self, name):
            pass

        def post_login(self, name, password):
            pass

    app = Flask(__name__)
    app.debug = True
    api = Api(app)
    api.add_resource(Hello)

    assert Hello.schema_inputs == validater.parse(sche_inputs)
    assert Hello.schema_outputs == validater.parse(sche_outputs)
    assert Hello.output_types == [Flask]


def test_base(app):
    with app.test_client() as c:
        assert 200 == c.get("/hello").status_code
        assert b"hello" == c.get("/hello").data
        with pytest.raises(ValueError) as exinfo:
            c.get("/hello/error")
        assert exinfo.value.args == ("error",)


def test_before_request(app):
    @app.api.before_request
    def before_request():
        return "before_request"

    with app.test_client() as c:
        assert b"before_request" == c.get("/hello").data
        assert b"before_request" == c.get("/hello/error").data
        assert 200 == c.get("/hello/error").status_code


def test_after_request(app):
    @app.api.after_request
    def after_request(rv, code, headers):
        return "after_request", 200, headers

    with app.test_client() as c:
        assert b"after_request" == c.get("/hello").data
        with pytest.raises(ValueError) as exinfo:
            c.get("/hello/error")
        assert exinfo.value.args == ("error",)


def test_error_handler(app):
    @app.api.error_handler
    def error_handler(ex):
        assert isinstance(ex, ValueError)
        assert ex.args == ('error',)
        return "error_hander"
    with app.test_client() as c:
        assert 200 == c.get("/hello").status_code
        assert b"hello" == c.get("/hello").data
        assert 200 == c.get("/hello/error").status_code
        assert b"error_hander" == c.get("/hello/error").data


def test_load_options():
    app = Flask(__name__)
    app.config.from_object("testdata.config")
    expect_configs = {"auth_header": "API_AUTH_HEADER", "auth_exp": 3000}
    options = load_options(
        {"auth_header": "auth_header"}, app, {"auth_exp": 3000})
    assert options == expect_configs


def test_custom_validaters():
    api = Api()

    def foo_validater(v):
        return (True, v)
    api.validater.add_validater("foo", foo_validater)
    assert "foo" in api.validater.validaters
    assert "foo" not in validater.default_validaters
    sche = api.validater.parse("foo&required")
    err, val = validater.validate('haha', sche)
    assert not err
    assert val == 'haha'
    err, val = api.validater.validate('haha', sche)
    assert not err
    assert val == 'haha'
    api.validater.remove_validater("foo")
    assert "foo" not in api.validater.validaters
