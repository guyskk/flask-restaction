# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import
from flask import Flask, current_app
from flask_restaction import exporters, exporter
from flask_restaction import Api, Resource
import json
import pytest


@exporter("text/html")
def export_string(data, code, header):
    return current_app.response_class(
        str(data), status=code, headers=header, mimetype='text/html')


def test_base():
    assert 'application/json' in exporters
    assert "text/html" in exporters


@pytest.fixture(scope="module")
def app():
    app = Flask(__name__)
    app.debug = True
    api = Api(app)

    class Hello(Resource):

        def get(self):
            return [123]

    api.add_resource(Hello)
    return app


def test_export(app):

    def get_text(c, url):
        return c.get(
            url, headers={"Accept":
                          "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"})

    def get_json(c, url):
        return c.get(
            url, headers={"Accept":
                          "application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"})
    with app.test_client() as c:
        resp = get_text(c, '/hello')
        assert b'[123]' == resp.data
        assert "text/html" in resp.headers["Content-Type"]
        resp = get_json(c, '/hello')
        assert b'[\n  123\n]\n' == resp.data
        assert "application/json" in resp.headers["Content-Type"]
        resp = c.get('/hello')
        assert b'[\n  123\n]\n' == resp.data
        assert "application/json" in resp.headers["Content-Type"]
