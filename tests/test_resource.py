
from flask import Flask, request, url_for
from flask_restaction import Api, Resource
import pytest
"""
blueprint.resource@action
resource@action
blueprint.resource
resource
"""


@pytest.fixture(scope="module")
def app():
    app = Flask(__name__)
    app.debug = True
    api = Api(app)

    class Hello(Resource):

        def get(self):
            return "hello"

        def post_login(self):
            return "login"

    class File(Resource):

        def get(self):
            return "file"

        def post_login(self):
            return "login"

    api.add_resource(Hello)
    api.add_resource(File, name="upload")

    return app


def test_hello(app):

    with app.test_request_context('/hello/login'):
        assert request.endpoint == 'hello@login'

    with app.test_request_context('/hello'):
        assert url_for("hello") == '/hello'
        assert url_for("hello@login") == '/hello/login'
        assert request.endpoint == 'hello'

    with app.test_client() as c:
        assert 'hello' == c.get('/hello').data
        assert "login" == c.post('/hello/login').data


def test_file(app):

    with app.test_request_context('/upload'):
        assert url_for("file") == '/upload'
        assert url_for("file@login") == '/upload/login'
        assert request.endpoint == 'file'

    with app.test_request_context('/upload/login'):
        assert request.endpoint == 'file@login'

    with app.test_client() as c:
        assert 'file' == c.get('/upload').data
        assert "login" == c.post('/upload/login').data
