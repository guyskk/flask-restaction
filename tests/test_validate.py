# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import

from flask import Flask, request, url_for
from flask_restaction import Api, Resource
from datetime import datetime
import pytest
out_obj = {"hello": "world"}


def set_out(obj):
    global out_obj
    out_obj = obj


@pytest.fixture(scope="module")
def app():
    app = Flask(__name__)
    app.debug = True
    api = Api(app)

    class Hello(Resource):
        schema_inputs = {
            "get": {"name": ("name&required&default='world'", "name")},
            "post_login": {"date": ("date&required", "date")},
        }
        schema_outputs = {
            "get": {"hello": ("unicode&required", "hello")}
        }

        def get(self, name):
            global out_obj
            return out_obj

        def post_login(self, date):
            global out_obj
            return out_obj

    api.add_resource(Hello)
    return app


def test_inputs(app):
    set_out({"hello": "world"})
    with app.test_client() as c:
        # treat "" as NULL then asign default value
        assert 200 == c.get("hello?name=").status_code
        assert b"world" in c.get("hello?name=").data
        assert 400 == c.get("hello?name=1").status_code
        assert 400 == c.get("hello?name=a1533gfdhgfh544y4yhb").status_code
        assert b"hello" in c.get("hello?name=a12345").data
        assert b"hello" in c.get("hello").data
        assert b"world" in c.get("hello").data
        assert b"hello" in c.post("hello/login", data={
            "date": datetime.utcnow().date().isoformat()
        }).data
        assert 400 == c.post("hello/login").status_code
        assert 400 == c.post("hello/login", data={
            "date": "fsdbdsgafd"
        }).status_code
        assert b"required" in c.post("hello/login", data={}).data


def test_outputs(app):
    with app.test_client() as c:

        set_out({"hello": "world"})
        assert b"hello" in c.get("hello").data

        set_out({"hello0": "world"})
        assert b"required" in c.get("hello").data

        set_out({"hello": 123})
        assert b"unicode" in c.get("hello").data

        set_out({})
        assert b"required" in c.get("hello").data

        set_out({"hello": "world"})
        assert b"hello" in c.get("hello").data

        assert b"world" in c.get("hello").data


def test_outputs_not_debug(app):
    """validate error will not cause HTTPException"""
    app.debug = False
    with app.test_client() as c:

        set_out({"hello": "world"})
        assert b"hello" in c.get("hello").data

        set_out({"hello0": "world"})
        assert b"required" in c.get("hello").data

        set_out({"hello": 123})
        assert b"unicode" in c.get("hello").data

        set_out({})
        assert b"required" in c.get("hello").data

        set_out({"hello": "world"})
        assert b"hello" in c.get("hello").data

        assert b"world" in c.get("hello").data
