from flask import Flask, request, url_for
from flask_restaction import Api, Resource
from datetime import datetime


import pdb; pdb.set_trace()  # breakpoint 61c8ca95 //
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


def test_base():
    app = Flask(__name__)
    app.debug = True
    api = Api(app)
    api.add_resource(Hello)

    # @api.before_request
    def api_before_request():
        return {"hello": "before_request"}

    # @api.after_request
    def api_after_request(data, code, headers):
        return {"hello": "after_request"}, code, headers

    # @api.error_handler
    def api_error_handler(ex):
        return {"hello": "error_handler"}
    assert api_before_request in api.before_request_funcs
    assert api_after_request in api.after_request_funcs
    assert api_error_handler == api.handle_error_func
