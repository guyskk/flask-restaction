#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function

from flask import Flask, Blueprint, g, url_for, request
from flask_restaction import Api, Resource
import validater
import pytest


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
        assert g.me["id"] is None


def test_blueprint():
    class Hello(Resource):

        def get(self):
            return "hello"

    app = Flask(__name__)
    app.debug = True
    bp = Blueprint("blueprint", __name__)
    api = Api(bp)
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
        assert g.me["id"] is None


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


def test_config():
    app = Flask(__name__)
    app.config.from_object("testdata.config")
    app.debug = True
    configs = ["auth_header",
               "auth_token_name", "auth_secret", "auth_alg", "auth_exp",
               "resjs_name", "resdocs_name", "bootstrap"]
    # "resource_json", "permission_json",  will be change to abs path
    bp = Blueprint("blueprint", __name__)
    api_bp = Api(bp)
    api_app = Api(app)
    api_no_app = Api()
    for k in configs:
        key = "API_" + k.upper()
        assert key in app.config
        assert app.config[key] == key
        assert hasattr(api_app, k)
        assert getattr(api_app, k) == key

        assert getattr(api_no_app, k) != key
        # inited with blue_print can't load configs
        assert getattr(api_bp, k) != key

    api_bp.config(app.config)
    for k in configs:
        key = "API_" + k.upper()
        assert getattr(api_bp, k) == key


def test_log_warning():
    """if permission_path not exists, should log warning"""
    app = Flask(__name__)
    api = Api(app)
    with app.test_client() as c:
        assert 404 == c.get("/").status_code


def test_testclient():
    class Hello(Resource):
        schema_inputs = {
            "get": {"name": "name&default='world'"}
        }
        schema_outputs = {
            "get": {"hello": "safestr&required"}
        }

        def get(self, name):
            return {"hello": name}

    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Hello)

    with api.test_client() as c:
        assert 200 == c.hello.get().code
        assert {"hello": "world"} == c.hello.get().rv

        assert 200 == c.hello.get({"name": "guyskk"}).code
        assert {"hello": "guyskk"} == c.hello.get({"name": "guyskk"}).rv

        assert 404 == c.hello.get_asd().code
        with pytest.raises(ValueError):
            c.asdfgh.get()

    # api did't inited
    with pytest.raises(AttributeError):
        api = Api()
        api.test_client()
