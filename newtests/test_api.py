#!/usr/bin/env python
# coding: utf-8

from flask import Flask
from flask import url_for
from flask import request
from flask_restaction import Api

import pytest


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.debug = True
    api = Api(app)

    class Hello:

        def get(self):
            return 'hello'

        def get_error(self):
            raise ValueError('error')

    api.add_resource(Hello)
    app.api = api
    return app


def test_hello_world():
    class Hello:
        """Hello world"""

        def get(self, name):
            """Get welcome message

            $input:
                name?str&escape&default="world": Your name
            $output:
                message?str&maxlen=60: welcome message
            """
            return {
                'message': 'Hello {}'.format(name)
            }

        def post(self, name):
            """Post welcome message

            $input:
                name?str&escape&default="anonym": name
            $output:
                message?str&maxlen=60: welcome message
            """
            return {
                'message': 'Hello {}'.format(name)
            }

    app = Flask(__name__)
    app.debug = True
    api = Api(app)
    api.add_resource(Hello)

    with app.test_request_context('hello'):
        assert request.endpoint == 'hello'
        assert url_for('hello') == '/hello'
    with app.test_client() as c:
        rv = c.get('hello')
        assert rv.status_code == 200
        assert b'Hello' in rv.data
    with app.test_client() as c:
        headers = {'Content-Type': 'application/json'}
        assert c.post('hello', headers=headers).status_code == 400
        assert c.post('hello', data={'name': 'me'},
                      headers=headers).status_code == 200
