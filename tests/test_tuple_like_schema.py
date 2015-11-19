# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import

from flask import Flask, request, url_for
from flask_restaction import Api, Resource, schema
from datetime import datetime
import pytest


@pytest.fixture(scope="module")
def api():
    app = Flask(__name__)
    app.debug = True
    api = Api(app)

    class Hello(Resource):
        name = "name&required", "world", "your name"
        date = "datetime&required", None, "date"
        hello = "unicode&required", None, "hello"

        schema_inputs = {
            "get": schema("name"),
            "post_login": schema("date"),
        }
        schema_outputs = {
            "get": schema("hello")
        }

        def get(self, name):
            return {"hello": name}

        def post_login(self, date):
            return {"hello": "world"}

    api.add_resource(Hello)

    # schema should be combine to dict after add_resource
    for k, v in Hello.schema_inputs.items():
        assert isinstance(v, dict)
    for k, v in Hello.schema_outputs.items():
        assert isinstance(v, dict)
    assert "name" in Hello.schema_inputs["get"]
    assert "date" in Hello.schema_inputs["post_login"]
    assert "hello" in Hello.schema_outputs["get"]

    return api


def test_schema_is_dict(api):
    schema_inputs = api.resources["hello"]["class"].schema_inputs
    schema_outputs = api.resources["hello"]["class"].schema_outputs
    for k, v in schema_inputs.items():
        assert isinstance(v, dict)
    for k, v in schema_outputs.items():
        assert isinstance(v, dict)
    assert schema_inputs["get"]["name"]["required"]
    assert "world" == schema_inputs["get"]["name"]["default"]
    assert schema_inputs["post_login"]["date"]["required"]
    assert schema_outputs["get"]["hello"]["required"]


def test_inputs(api):
    with api.app.test_client() as c:
        assert b"hello" in c.get("/hello?name=guyskk").data
        assert b"guyskk" in c.get("/hello?name=guyskk").data
        assert 400 == c.post("/hello/login").status_code
        assert b"required" in c.post("/hello/login").data
        assert 200 == c.post("/hello/login", data={"date": "2015-11-03 21:21:50"}).status_code
        assert b"hello" in c.post("/hello/login", data={"date": "2015-11-03 21:21:50"}).data
