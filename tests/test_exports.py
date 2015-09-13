from flask import Flask, current_app
from flask_restaction import exporters, exporter
from flask_restaction import Api, Resource
import json


@exporter("text/html")
def export_string(data, code, header):
    return current_app.response_class(
        str(data), status=code, headers=header, mimetype='text/html')


def test_base():
    assert 'application/json' in exporters
    assert "text/html" in exporters


app = Flask(__name__)
app.debug = True
api = Api(app)


class Hello(Resource):

    def get(self):
        return ["hello"]

api.add_resource(Hello)


def test_export():

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
        assert str(['hello']) == resp.data
        assert "text/html" in resp.headers["Content-Type"]
        resp = get_json(c, '/hello')
        assert ['hello'] == json.loads(resp.data)
        assert "application/json" in resp.headers["Content-Type"]
        resp = c.get('/hello')
        assert ['hello'] == json.loads(resp.data)
        assert "application/json" in resp.headers["Content-Type"]
