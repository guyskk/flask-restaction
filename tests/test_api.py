from flask import Flask, request, url_for
from flask_restaction import Api, Resource
from datetime import datetime
import pytest

out_obj = {u"hello": u"world"}
event_handler_config = [True, True, True]


def set_out(obj):
    global out_obj
    out_obj = obj


def config(*config):
    global event_handler_config
    event_handler_config = list(config)


@pytest.fixture(scope="module")
def appapi():
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

    app = Flask(__name__)
    app.debug = True
    api = Api(app)
    api.add_resource(Hello)

    @api.before_request
    def api_before_request():
        if event_handler_config[0]:
            return {"hello": "before_request"}
        else:
            return None

    @api.after_request
    def api_after_request(data, code, headers):
        if event_handler_config[1]:
            return {"hello": "after_request"}, code, headers
        else:
            return data, code, headers

    @api.error_handler
    def api_error_handler(ex):
        if event_handler_config[2]:
            return {"hello": "error_handler"}
        else:
            return None

    return app, api


def test_base(appapi):
    app, api = appapi

    with app.test_client() as c:
        config(True, True, True)
        assert "after_request" in c.get("/hello", query_string={"name": "haha"}).data
        assert "after_request" in c.get("/hello", query_string={"name": "ha!@#ha"}).data
        config(True, False, True)
        assert "before_request" in c.get("/hello", query_string={"name": "haha"}).data
        assert "before_request" in c.get("/hello", query_string={"name": "ha!@#ha"}).data
        config(False, False, True)
        assert "world" in c.get("/hello", query_string={"name": "haha"}).data
        assert "re_name" in c.get("/hello", query_string={"name": "ha!@#ha"}).data
        config(False, True, True)
        assert "after_request" in c.get("/hello", query_string={"name": "haha"}).data
        assert "after_request" in c.get("/hello", query_string={"name": "ha!@#ha"}).data
