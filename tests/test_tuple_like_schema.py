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
    schema_inputs = api.resources["hello"]["schema_inputs"]
    schema_outputs = api.resources["hello"]["schema_outputs"]
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


def test_schema():
    """"""
    leaf1 = "+int&required", 1, "leaf1 desc"
    leaf2 = "unicode&required"
    leaf3 = "unicode", None, "article table of content"

    branch1 = schema("leaf1", "leaf2")
    branch2 = schema("branch1", "leaf3")

    flower = schema(["branch1"])
    tree = schema(["branch2"])

    forest1 = schema(["tree"])
    forest2 = schema([["branch2"]])
    park = schema("tree", "flower")

    scope = locals()

    # import json

    # def pp(obj):
    #     print json.dumps(obj, ensure_ascii=False, indent=4)

    # pp(branch1(scope))
    # pp(branch2(scope))

    # pp(flower(scope))
    # pp(tree(scope))

    # pp(forest1(scope))
    # pp(forest2(scope))
    # pp(park(scope))

    branch1 = branch1(scope)
    assert branch1["leaf1"]["validate"] == "+int"
    assert branch1["leaf2"]["validate"] == "unicode"

    branch2 = branch2(scope)
    assert branch2["branch1"]["leaf1"]["validate"] == "+int"
    assert branch2["leaf3"]["validate"] == "unicode"

    flower = flower(scope)
    assert len(flower) == 1
    assert flower[0]["leaf1"]["validate"] == "+int"

    tree = tree(scope)
    assert len(tree) == 1
    assert tree[0]["branch1"]["leaf1"]["validate"] == "+int"
    assert tree[0]["leaf3"]["validate"] == "unicode"

    forest1 = forest1(scope)
    forest2 = forest2(scope)
    assert forest1[0][0]["leaf3"]["validate"] == "unicode"
    assert forest1 == forest2

    park = park(scope)
    assert park["tree"][0]["branch1"]["leaf1"]["validate"] == "+int"
    assert park["flower"][0]["leaf1"]["validate"] == "+int"
