from flask import Flask, request, url_for
from flask_restaction import Api, Resource
from datetime import datetime

app = Flask(__name__)
app.debug = True
api = Api(app)

out_obj = {"hello": "world"}


def set_out(obj):
    global out_obj
    out_obj = obj


class Hello(Resource):
    schema_name = ("name", {
        "desc": "name",
        "required": True,
        "validate": "re_name",
        "default": "world"
    })
    schema_date = ("date", {
        "desc": "date",
        "required": True,
        "validate": "datetime",
    })
    schema_hello = ("hello", {
        "desc": "hello",
        "required": True,
        "validate": "unicode",
    })
    schema_inputs = {
        "get": dict([schema_name]),
        "post_login": dict([schema_date]),
    }
    schema_outputs = {
        "get": dict([schema_hello])
    }

    def get(self, name):
        global out_obj
        return out_obj

    def post_login(self, date):
        global out_obj
        return out_obj

api.add_resource(Hello)


def test_inputs():
    set_out({"hello": u"world"})
    with app.test_client() as c:
        assert 400 == c.get("hello?name=").status_code
        assert 400 == c.get("hello?name=1").status_code
        assert 400 == c.get("hello?name=a1533gfdhgfh544y4yhb").status_code
        assert "hello" in c.get("hello?name=a12345").data
        assert "hello" in c.get("hello").data
        assert "world" in c.get("hello").data
        assert "hello" in c.post("hello/login", data={
            "date": datetime.now().isoformat()
        }).data
        assert 400 == c.post("hello/login").status_code
        assert 400 == c.post("hello/login", data={
            "date": "fsdbdsgafd"
        }).status_code
        assert "required" in c.post("hello/login", data={}).data


def test_outputs():
    with app.test_client() as c:

        set_out({"hello": u"world"})
        assert "hello" in c.get("hello").data

        set_out({"hello0": u"world"})
        assert "required" in c.get("hello").data

        set_out({"hello": "world"})
        assert "unicode" in c.get("hello").data

        set_out({})
        assert "required" in c.get("hello").data

        set_out({u"hello": u"world"})
        assert "hello" in c.get("hello").data

        assert "world" in c.get("hello").data


def test_outputs_not_debug():
    app.debug = False
    with app.test_client() as c:

        set_out({"hello": u"world"})
        assert "hello" in c.get("hello").data

        set_out({"hello0": u"world"})
        assert "required" not in c.get("hello").data
        assert "error" in c.get("hello").data

        set_out({"hello": "world"})
        assert "unicode" not in c.get("hello").data
        assert "error" in c.get("hello").data

        set_out({})
        assert "required" not in c.get("hello").data
        assert "error" in c.get("hello").data

        set_out({u"hello": u"world"})
        assert "hello" in c.get("hello").data

        assert "world" in c.get("hello").data
