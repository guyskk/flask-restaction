import importlib
import sys

import pytest
from flask_restaction import Res
from requests import HTTPError

sys.path.append('./server')
app = importlib.import_module("index").app


@pytest.fixture(params=[
    {"url_prefix": "http://127.0.0.1:5000"},
    {"test_client": app.test_client}
])
def res(request):
    return Res(**request.param)


def test_basic(res):
    data = {"name": "kk"}
    expect = {"hello": "kk"}
    assert res.test.get(data) == expect
    assert res.test.post(data) == expect
    assert res.test.post_name(data) == expect
    assert res.test.put(data) == expect
    assert res.test.patch(data) == expect
    assert res.test.delete(data) == expect


def test_ajax(res):
    assert res.ajax("/")["test"]["get"] is not None


@pytest.mark.parametrize("code", [404, 403, 401, 400, 500])
def test_error(res, code):
    with pytest.raises(HTTPError) as exinfo:
        f = getattr(res.test, "get_%d" % code)
        f()
    assert exinfo.value.response.status_code == code


def test_302(res):
    assert res.test.get_302({"name": "kk"}) == {"hello": "world"}


def test_auth(res):
    with pytest.raises(HTTPError):
        res.test.get_me()
    assert res.test.post_login({"name": "admin"})
    assert res.test.get_me()["name"] == "admin"
    assert res.test.post_login({"name": "kk"})
    assert res.test.get_me()["name"] == "kk"


def test_api_meta_view():
    with app.test_client() as c:
        resjs = c.get("/?f=res.js")
        assert resjs.status_code == 200
        assert resjs.headers["Content-Type"] == "application/javascript"
        resminjs = c.get("/?f=res.min.js")
        assert resminjs.status_code == 200
        assert resminjs.headers["Content-Type"] == "application/javascript"
        resjs2 = c.get("/?f=res.js")
        assert resjs.data == resjs2.data
        resminjs2 = c.get("/?f=res.min.js")
        assert resminjs.data == resminjs2.data
        resp = c.get("/?f=docs.min.js")
        assert resp.status_code == 200
        resp = c.get("/?f=docs.min.css")
        assert resp.status_code == 200
        resp = c.get("/?f=unknown.js")
        assert resp.status_code == 404
