import json
import pytest
from flask import Flask, Blueprint, url_for, request
from flask_restaction import Api


def resp_json(resp):
    return json.loads(resp.data.decode("utf-8"))


@pytest.fixture()
def app():
    app = Flask(__name__)
    api = Api(app)

    class Hello:

        def get(self):
            return 'hello'

        def get_error(self):
            raise ValueError('error')

    api.add_resource(Hello)
    return app.test_client()


def test_no_input_schema():
    app = Flask(__name__)
    api = Api(app)

    class Hello:

        def get(self):
            """Get hello

            $output:
                message?str: welcome message
            """
            name = request.args.get("name")
            return {"key": name}
    api.add_resource(Hello)

    meta_action = api.meta["hello"]["get"]
    assert meta_action.keys() == {"$output", "$desc"}
    assert meta_action["$output"] == {"message?str": "welcome message"}
    assert meta_action["$desc"] == "Get hello"

    c = app.test_client()
    resp = c.get("/hello?name=kk")
    assert resp.status_code == 500
    assert resp_json(resp)["error"] == "InvalidData"


def test_no_output_schema():
    pass


def test_no_docstring():
    pass


def test_docstring_no_schema():
    pass


def test_hello_world():
    class Hello:
        """Hello world test"""

        def get(self, name):
            """Get Hello world message

            $input:
                name?str&escape&default="world": Your name
            $output:
                message?str&maxlen=60: welcome message
            """
            return {
                'message': 'Hello {}'.format(name)
            }

        def post(self, name):
            """Post message

            $input:
                name?str&escape&default="anonym": name
            $output:
                message?str&maxlen=60: post echo
            """
            return {
                'message': 'post by {}'.format(name)
            }

        def put(self, name):
            """Put message

            $input:
                name?str&escape&default="anonym": name
            $output:
                message?str&maxlen=60: put echo
            """
            return {
                'message': 'put by {}'.format(name)
            }

    app = Flask(__name__)
    app.debug = True
    api = Api(app)
    api.add_resource(Hello)

    with app.test_request_context('hello'):
        assert request.endpoint == 'hello'
        assert url_for('hello') == '/hello'
    with app.test_client() as c:
        headers = {'Content-Type': 'application/json'}
        good_params = dict(data='{"name":"tester"}', headers=headers)
        null_params = dict(data='{"name":null}', headers=headers)
        bad_params = dict(data='x', headers=headers)
        empty_params = dict(data='null', headers=headers)
        assert c.get('hello').status_code == 200
        assert b'world' in c.get('hello').data
        assert b'tester' in c.get('hello?name=tester').data

        assert c.post('hello', **good_params).status_code == 200
        assert c.post('hello', **null_params).status_code == 200
        assert b'anonym' in c.post('hello', **null_params).data
        assert c.post('hello', **bad_params).status_code == 400
        assert c.post('hello', **empty_params).status_code == 400

        assert c.put('hello', **good_params).status_code == 200


def test_blueprint():
    class Hello:
        """Blueprint test"""

        def get(self):
            """Get Hello world message
            """
            return {'message': 'Hello world'}

    app = Flask(__name__)
    app.debug = True
    bp = Blueprint('blueprint', __name__)
    api = Api(bp)
    api.add_resource(Hello)
    app.register_blueprint(bp, url_prefix='/api')

    with app.test_request_context('/api/hello'):
        assert request.endpoint == 'blueprint.hello'
        assert url_for('blueprint.hello') == '/api/hello'
    with app.test_client() as c:
        rv = c.get('/api/hello')
        assert b'Hello' in rv.data
