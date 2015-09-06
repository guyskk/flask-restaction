import os
from flask import Flask, request, url_for
from flask_restaction import Api, Resource
"""
blueprint.resource@action
resource@action
blueprint.resource
resource
"""

app = Flask(__name__)
app.debug = True
api = Api(app)


@api.resource()
class Hello(Resource):

    def get(self):
        return "hello"

    def post_login(self):
        return "login"


@api.resource()
class File(Resource):

    def get(self):
        return "get file"

    def put(self):
        return "put file"

    def post(self):
        return "post file"


def test_resource():

    # import pdb
    # pdb.set_trace()
    # api.add_resource(Hello)
    client = app.test_client()
    with app.test_request_context('/hello'):
        # import pdb
        # pdb.set_trace()
        assert url_for("hello") == '/hello'
        assert url_for("hello@login") == '/hello/login'

    with app.test_request_context('/hello/login'):
        assert request.endpoint == 'hello@login'
        assert True

    assert 'hello' == client.get('/hello').data
    assert "login" == client.post('/hello/login').data


def test_resource2():
    app = Flask(__name__)
    app.debug = True
    api = Api(app)

    @api.resource(name="hi")
    class Hello(Resource):

        def get(self, *args, **kvargs):
            # import pdb
            # pdb.set_trace()
            return "hello"

        def post_login(self, *args, **kvargs):
            return "login"

    # import pdb
    # pdb.set_trace()
    # api.add_resource(Hello)
    client = app.test_client()
    with app.test_request_context('/hi'):
        # import pdb
        # pdb.set_trace()
        assert url_for("hi") == '/hi'
        assert url_for("hi@login") == '/hi/login'

    with app.test_request_context('/hi/login'):
        assert request.endpoint == 'hi@login'
        assert True

    assert 'hello' == client.get('/hi').data
    assert "login" == client.post('/hi/login').data
