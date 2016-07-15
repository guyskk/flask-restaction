import json
import yaml
import pytest
from validater import Invalid
from validater.validaters import handle_default_optional_desc
from flask import Flask, Blueprint, url_for, request, make_response, g
from flask_restaction import exporter
from flask_restaction.api import (
    Api, abort, unpack, export, parse_docs,
    get_request_data, parse_request
)
from werkzeug.exceptions import BadRequest


def resp_json(resp):
    return json.loads(resp.data.decode("utf-8"))


def test_abort():
    app = Flask(__name__)

    @app.route("/")
    def index():
        abort(400, {"error": "AbortTest"})

    @app.route("/headers")
    def headers():
        abort(403, {"error": "AbortHeadersTest"}, {"Authorization": "XXXX"})

    with app.test_client() as c:
        resp = c.get("/")
        assert resp.status_code == 400
        assert resp_json(resp) == {"error": "AbortTest"}

        resp = c.get("/headers")
        assert resp.status_code == 403
        assert resp_json(resp) == {"error": "AbortHeadersTest"}
        assert resp.headers["Authorization"] == "XXXX"


def test_unpack():
    assert unpack("rv") == ("rv", None, None)
    assert unpack(123) == (123, None, None)
    assert unpack({}) == ({}, None, None)
    assert unpack([]) == ([], None, None)

    assert unpack(("rv", 200)) == ("rv", 200, None)
    assert unpack(("rv", 200, {})) == ("rv", 200, {})
    assert unpack(("rv", 200, [])) == ("rv", 200, [])

    assert unpack(("rv", {})) == ("rv", None, {})
    assert unpack(("rv", [])) == ("rv", None, [])

    assert unpack(("rv", {}, 200)) == ("rv", 200, {})
    assert unpack(("rv", [], 200)) == ("rv", 200, [])


@pytest.mark.parametrize("rv, code, headers", [
    ({"message": "hello"}, 200, None),
    ({"message": "中文"}, 400, None),
    (123, 200, None),
    ("123", 200, None),
    (None, 200, None),
    ("rv", 200, {"Authorization": "XXX"}),
    ("rv", 200, [("Authorization", "XXX")])
])
def test_export(rv, code, headers):
    app = Flask(__name__)
    with app.test_request_context("/"):

        resp = export(rv)
        assert resp.status_code == 200

        resp = export(rv, code)
        assert resp.mimetype == "application/json"
        assert resp.status_code == code
        assert resp_json(resp) == rv

        if headers is not None:
            resp = export(rv, None, headers)
            if isinstance(headers, dict):
                for k, v in headers.items():
                    assert resp.headers[k] == v
            else:
                for k, v in headers:
                    assert resp.headers[k] == v


def test_export_response():
    app = Flask(__name__)
    with app.test_request_context("/"):
        resp = make_response("hello")

        resp = export(resp)
        assert resp.mimetype == "text/html"
        assert resp.status_code == 200
        assert resp.data == b"hello"

        resp = export(resp, 400)
        assert resp.mimetype == "text/html"
        assert resp.status_code == 400
        assert resp.data == b"hello"


def test_export_custom():
    app = Flask(__name__)

    @exporter("text/html")
    def export_html(rv, code, headers):
        return make_response(rv, code, headers)

    accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    with app.test_request_context(headers={"Accept": accept}):
        resp = export("hello world")
        assert resp.mimetype == "text/html"
        assert resp.data == b"hello world"


def test_parse_docs():
    def f_no_docs():
        pass
    assert parse_docs(f_no_docs.__doc__, ["$input"]) == {}

    def f_no_content():
        """"""
    assert parse_docs(f_no_content.__doc__, ["$input"]) == {"$desc": ""}

    def f_empty_content():
        """        """
    assert parse_docs(f_empty_content.__doc__, ["$input"]) == {"$desc": ""}

    def f_no_yaml():
        """Hello World"""
    assert parse_docs(f_no_yaml.__doc__, ["$input"]) == {
        "$desc": "Hello World"
    }

    def f_no_marks():
        """
        Hello World

        No marks
        """
    assert parse_docs(f_no_marks.__doc__, ["$input"]) == {
        "$desc": "Hello World\n\nNo marks"
    }


def test_parse_docs_has_yaml():
    def f():
        """
        Hello

        name: kk
        email: guyskk@qq.com
        """
    assert parse_docs(f.__doc__, marks=[]) == {
        "$desc": "Hello\n\nname: kk\nemail: guyskk@qq.com"
    }
    assert parse_docs(f.__doc__, marks=["unknown"]) == {
        "$desc": "Hello\n\nname: kk\nemail: guyskk@qq.com"
    }
    assert parse_docs(f.__doc__, marks=["email"]) == {
        "$desc": "Hello\n\nname: kk",
        "email": "guyskk@qq.com"
    }
    assert parse_docs(f.__doc__, marks=["name"]) == {
        "$desc": "Hello",
        "name": "kk",
        "email": "guyskk@qq.com"
    }
    assert parse_docs(f.__doc__, marks=["name", "email"]) == {
        "$desc": "Hello",
        "name": "kk",
        "email": "guyskk@qq.com"
    }


def test_parse_docs_invalid_yaml():
    def f_invalid_syntax():
        """
        $input:
          name: kk
            email: guyskk@qq.com
        """
    with pytest.raises(yaml.YAMLError):
        parse_docs(f_invalid_syntax.__doc__, ["$input"])

    def f_invalid_yaml_char():
        """
        $input:
            userid: @userid
        """
    with pytest.raises(yaml.YAMLError):
        parse_docs(f_invalid_yaml_char.__doc__, ["$input"])

    def f_invalid_char_quoted():
        """
        $input:
            userid: "@userid"
        """
    assert parse_docs(f_invalid_char_quoted.__doc__, ["$input"]) == {
        "$desc": "",
        "$input": {
            "userid": "@userid"
        }
    }


def test_get_request_data():
    app = Flask(__name__)
    with app.test_client() as c:
        c.get("/", query_string={"name": "kk"})
        assert get_request_data().get("name") == "kk"
        assert get_request_data()["name"] == "kk"

        c.get("/?name=kk")
        assert get_request_data().get("name") == "kk"
        assert get_request_data()["name"] == "kk"

        c.post("/?name=xx", data={"name": "kk"})
        assert get_request_data().get("name") == "kk"
        assert get_request_data()["name"] == "kk"

        headers = {"Content-Type": "application/json"}
        c.post("/?name=xx", data='{"name": "kk"}', headers=headers)
        assert get_request_data().get("name") == "kk"
        assert get_request_data()["name"] == "kk"

        with pytest.raises(BadRequest):
            c.post("/?name=xx", data='{"name": kk}', headers=headers)
            get_request_data()


def test_parse_request():
    app = Flask(__name__)

    @app.route("/", endpoint="index", methods=["GET", "POST"])
    def index():
        return "123"

    @app.route("/page", endpoint="index@page")
    def index_page():
        return "123"

    @app.route("/blueprint/page", endpoint="blueprint.index@page")
    def blueprint_index_page():
        return "123"

    with app.test_client() as c:
        c.get("/")
        assert parse_request() == ("index", "get")
        c.post("/")
        assert parse_request() == ("index", "post")

        c.get("/page")
        assert parse_request() == ("index", "get_page")

        c.get("/blueprint/page")
        assert parse_request() == ("index", "get_page")


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


def test_no_schema():
    app = Flask(__name__)
    api = Api(app)

    class Hello:

        def get(self):
            """
            Get hello

            Welcome
            """
            return {}
    api.add_resource(Hello)

    with app.test_client() as c:
        resp = c.get("/hello?name=kk")
        assert resp.status_code == 200
        assert resp_json(resp) == {}


def test_no_input_schema():
    app = Flask(__name__)
    api = Api(app)

    class Hello:

        def get(self):
            """
            Get hello

            $output:
                message?str: welcome message
            """
            return {}
    api.add_resource(Hello)

    with app.test_client() as c:
        resp = c.get("/hello?name=kk")
        assert resp.status_code == 500
        assert resp_json(resp)["error"] == "InvalidData"


def test_no_output_schema():
    app = Flask(__name__)
    api = Api(app)

    class Hello:

        def get(self, userid):
            """Get hello

            $input:
                userid?int: UserID
            """
            return {"message": userid}
    api.add_resource(Hello)

    with app.test_client() as c:
        resp = c.get("/hello?userid=123")
        assert resp.status_code == 200
        assert resp_json(resp) == {
            "message": 123
        }
        resp = c.get("/hello?userid=kk")
        assert resp.status_code == 400
        assert resp_json(resp)["error"] == "InvalidData"


def test_input_output_schema():
    app = Flask(__name__)
    api = Api(app)

    class Welcome:

        def __init__(self, userid):
            self.userid = userid
            self.message = "Hi, %d" % userid

    class Hello:

        def get(self, userid):
            """Get hello

            $input:
                userid?int: UserID
            $output:
                message?str: Welcome message
            """
            return {"message": "Hi, %d" % userid}

        def post(self, userid):
            """Get hello

            $input:
                userid?int: UserID
            $output:
                message?str: Welcome message
            """
            return Welcome(userid)

    api.add_resource(Hello)

    with app.test_client() as c:
        resp = c.get("/hello?userid=123")
        assert resp.status_code == 200
        assert resp_json(resp) == {"message": "Hi, 123"}

        resp = c.post("/hello", data={"userid": 123})
        assert resp.status_code == 200
        assert resp_json(resp) == {"message": "Hi, 123"}

        headers = {"Content-Type": "application/json"}
        resp = c.post("/hello", data='{"userid": 123}', headers=headers)
        assert resp.status_code == 200
        assert resp_json(resp) == {"message": "Hi, 123"}


def test_helloworld():
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

        def get_message(self):
            pass

        def post(self, name):
            """Post message

            $input:
                name?str&escape&default="unknown": name
            $output:
                message?str&maxlen=60: post echo
            """
            return {
                'message': 'post by {}'.format(name)
            }

        def put(self, name):
            """Put message

            $input:
                name?str&escape&default="unknown": name
            $output:
                message?str&maxlen=60: put echo
            """
            return {
                'message': 'put by {}'.format(name)
            }

    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Hello)

    with app.test_request_context('/hello'):
        assert request.endpoint == 'hello'
        assert url_for('hello') == '/hello'

    with app.test_request_context('/hello/message'):
        assert request.endpoint == 'hello@message'
        assert url_for('hello@message') == '/hello/message'

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
        assert b'unknown' in c.post('hello', **null_params).data
        assert c.post('hello', **bad_params).status_code == 400
        assert c.post('hello', **empty_params).status_code == 400

        assert c.put('hello', **good_params).status_code == 200


def test_blueprint():
    class Hello:
        """Blueprint test"""

        def get(self, name):
            """
            Get Hello world message

            $input:
                name?str: Your name
            """
            return {'message': 'Hello %s' % name}

        def get_message(self):
            pass

    app = Flask(__name__)
    bp = Blueprint('blueprint', __name__)
    api = Api(bp)
    api.add_resource(Hello)
    app.register_blueprint(bp, url_prefix='/api')

    with app.test_request_context('/api/hello'):
        assert request.endpoint == 'blueprint.hello'
        assert url_for('blueprint.hello') == '/api/hello'

    with app.test_request_context('/api/hello/message'):
        assert request.endpoint == 'blueprint.hello@message'
        assert url_for('blueprint.hello@message') == '/api/hello/message'

    with app.test_client() as c:
        resp = c.get('/api/hello?name=kk')
        assert resp.status_code == 200
        assert resp_json(resp) == {
            "message": "Hello kk"
        }

        resp = c.get('/api/hello')
        assert resp.status_code == 400
        assert resp_json(resp)["error"] == "InvalidData"


def test_validaters():

    @handle_default_optional_desc
    def even_validater():
        def validater(value):
            try:
                i = int(value)
            except:
                raise Invalid("invalid int")
            if i % 2 == 0:
                return i
            else:
                raise Invalid("not even number")
        return validater

    app = Flask(__name__)
    api = Api(app, validaters={"even": even_validater})

    class Test:

        def get(self, number):
            """
            $input:
                number?even: even number
            """
            return {
                "number": number
            }
    api.add_resource(Test)
    with app.test_client() as c:
        resp = c.get("/test?number=2")
        assert resp.status_code == 200
        resp = c.get("/test?number=3")
        assert resp.status_code == 400
        assert resp_json(resp)["error"] == "InvalidData"


def test_metafile(tmpdir):
    metafile = tmpdir.join("meta.json")
    json.dump({"$xxx": "test", "$roles": {}}, metafile.open("w"))
    app = Flask(__name__)
    api = Api(app, metafile=metafile.strpath)

    class Hello:
        """docstring for Hello"""

        def get(self):
            """Get hello"""
    api.add_resource(Hello)

    with app.test_client() as c:
        resp = c.get("/")
        assert resp.status_code == 200
        assert resp_json(resp)["$xxx"] == "test"
        assert resp_json(resp)["$roles"] == {}
        assert resp_json(resp)["hello"]["$desc"] == "docstring for Hello"
        assert resp_json(resp)["hello"]["get"]["$desc"] == "Get hello"


def test_auth(tmpdir):
    metafile = tmpdir.join("meta.json")
    json.dump({
        "$desc": "test",
        "$roles": {
            "admin": {
                "hello": ["get", "post"]
            },
            "guest": {
                "hello": ["post"]
            }
        }
    }, metafile.open("w"))

    app = Flask(__name__)
    app.secret_key = "secret_key"
    api = Api(app, metafile=metafile.strpath)

    @api.get_role
    def get_role(token):
        g.name = None
        if token and token["name"] == "kk":
            g.name = token["name"]
            return "admin"
        else:
            return "guest"

    class Hello:

        def __init__(self, api):
            self.api = api

        def get(self):
            """
            Get Name

            $output:
                name?str&optional: Your name
            """
            return {"name": g.name}

        def post(self, name):
            """
            Generate Token

            $input:
                name?str: Your name
            """
            headers = self.api.gen_auth_headers({"name": name})
            return "OK", headers

    api.add_resource(Hello, api)
    auth_header = api.meta["$auth"]["header"]

    with app.test_client() as c:
        resp = c.get("/hello")
        assert resp.status_code == 403

        resp = c.post("/hello", data={"name": "abc"})
        assert resp.status_code == 200
        headers = {auth_header: resp.headers[auth_header]}
        resp = c.get("/hello", headers=headers)
        assert resp.status_code == 403
        assert resp_json(resp)["error"] == "PermissionDeny"
        assert "guest" in resp_json(resp)["message"]

        resp = c.post("/hello", data={"name": "kk"})
        assert resp.status_code == 200
        headers = {auth_header: resp.headers[auth_header]}
        resp = c.get("/hello", headers=headers)
        assert resp.status_code == 200
        assert resp_json(resp) == {"name": "kk"}


def test_docs_and_shared_schema():
    docs = """
    Hello World

    $shared:
        userid: int&min=0
    """
    app = Flask(__name__)
    api = Api(app, docs=docs)
    assert api.meta["$desc"] == "Hello World"
    assert api.meta["$shared"] == {"userid": "int&min=0"}

    class Hello:
        """
        docstring for Hello

        $shared:
            name: str
        """

        def get(self, userid, name):
            """
            Test shared schema

            $input:
                userid@userid: UserID
                name@name: UserName
            """
            return {
                "userid": userid,
                "name": name
            }
    api.add_resource(Hello)

    with app.test_client() as c:
        resp = c.get("/hello?userid=123&name=kk")
        assert resp.status_code == 200
        assert resp_json(resp) == {
            "userid": 123,
            "name": "kk"
        }
        resp = c.get("/hello?userid=abc&name=kk")
        assert resp.status_code == 400
        assert resp_json(resp)["error"] == "InvalidData"
        assert "userid" in resp_json(resp)["message"]


def test_before_request():
    app = Flask(__name__)
    api = Api(app)

    class Hello:

        def get(self):
            return "Hello World"
    api.add_resource(Hello)

    @api.before_request
    def before_request():
        return "before_request"

    with app.test_client() as c:
        resp = c.get("/hello")
        assert resp.status_code == 200
        assert resp_json(resp) == "before_request"


def test_after_request():
    app = Flask(__name__)
    api = Api(app)

    class Hello:

        def get(self):
            return "Hello World"
    api.add_resource(Hello)

    @api.after_request
    def after_request(rv, code, headers):
        return "%s after_request" % rv, code, headers

    with app.test_client() as c:
        resp = c.get("/hello")
        assert resp.status_code == 200
        assert resp_json(resp) == "Hello World after_request"


def test_error_handler():
    app = Flask(__name__)
    api = Api(app)

    class Hello:

        def get(self):
            raise ValueError("bug")
    api.add_resource(Hello)

    @api.error_handler
    def error_handler(ex):
        return "error_handler %s" % ex.args[0]

    with app.test_client() as c:
        resp = c.get("/hello")
        assert resp.status_code == 200
        assert resp_json(resp) == "error_handler bug"
