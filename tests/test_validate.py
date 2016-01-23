#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function

from flask import Flask, request, url_for
from flask_restaction import Api, Resource
from datetime import datetime
import pytest
import json


@pytest.fixture(scope="module")
def app():
    app = Flask(__name__)
    app.debug = True
    api = Api(app)

    class User(object):

        def __init__(self, name):
            self.name = name

    class Hello(Resource):
        name = "name&required&default='world'"
        date_in = {'validater': 'datetime',
                   'input': True,
                   'default': datetime.utcnow}
        date_out = 'datetime&required&output'
        schema_inputs = {
            "get": {"name": name},
            "get_user": {"name": name},
            "post": {"date": date_in}}
        schema_outputs = {
            "get": {"hello": "unicode&required"},
            "get_user": {"user": {"name": name}},
            "post": {"date": date_out}
        }
        output_types = [User]

        def get(self, name):
            return {'hello': name}

        def get_user(self, name):
            return {'user': User(name)}

        def post(self, date):
            return {'date': date}

    api.add_resource(Hello)
    return app


def test_get(app):
    with app.test_client() as c:
        resp = c.get("/hello?name=")
        assert 200 == resp.status_code
        assert {'hello': 'world'} == json.loads(resp.data)

        resp = c.get("/hello")
        assert 200 == resp.status_code
        assert {'hello': 'world'} == json.loads(resp.data)

        resp = c.get("/hello?name=abc123")
        assert 200 == resp.status_code
        assert {'hello': 'abc123'} == json.loads(resp.data)

        resp = c.get("/hello?name=1")
        assert 400 == resp.status_code
        assert 'name' in json.loads(resp.data)

        resp = c.get("/hello?name=中文")
        assert 400 == resp.status_code
        assert 'name' in json.loads(resp.data)


def test_get_user(app):
    with app.test_client() as c:
        resp = c.get("/hello/user?name=")
        assert 200 == resp.status_code
        assert {'name': 'world'} == json.loads(resp.data)['user']

        resp = c.get("/hello/user")
        assert 200 == resp.status_code
        assert {'name': 'world'} == json.loads(resp.data)['user']

        resp = c.get("/hello/user?name=abc123")
        assert 200 == resp.status_code
        assert {'name': 'abc123'} == json.loads(resp.data)['user']

        resp = c.get("/hello/user?name=1")
        assert 400 == resp.status_code
        assert 'name' in json.loads(resp.data)

        resp = c.get("/hello/user?name=中文")
        assert 400 == resp.status_code
        assert 'name' in json.loads(resp.data)


def test_post(app):
    with app.test_client() as c:
        data = {"date": "2016-01-22T12:59:59.000599Z"}
        resp = c.post("/hello", data=data)
        assert 200 == resp.status_code
        assert data == json.loads(resp.data)

        resp = c.post("/hello")
        assert 200 == resp.status_code
        assert 'date' in json.loads(resp.data)

        data = {"date": "2016-01-22"}
        resp = c.post("/hello", data=data)
        assert 400 == resp.status_code
        assert 'date' in json.loads(resp.data)

        resp = c.post("/hello")
        assert 200 == resp.status_code
        assert 'date' in json.loads(resp.data)
