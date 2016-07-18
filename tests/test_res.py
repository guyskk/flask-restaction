from flask_restaction import Res
import pytest
from requests import HTTPError

res = Res("http://127.0.0.1:5000")


def test_basic():
    data = {"name": "kk"}
    expect = {"hello": "kk"}
    assert res.test.get(data) == expect
    assert res.test.post(data) == expect
    assert res.test.post_name(data) == expect
    assert res.test.put(data) == expect
    assert res.test.patch(data) == expect
    assert res.test.delete(data) == expect


def test_ajax():
    assert res.ajax("/")["test"]["get"] is not None


@pytest.mark.parametrize("code", [404, 403, 401, 400, 500])
def test_error(code):
    with pytest.raises(HTTPError) as exinfo:
        f = getattr(res.test, "get_%d" % code)
        f()
    assert exinfo.value.response.status_code == code


def test_302():
    assert res.test.get_302({"name": "kk"}) == {"hello": "world"}


def test_auth():
    with pytest.raises(HTTPError):
        res.test.get_me()
    assert res.test.post_login({"name": "admin"})
    assert res.test.get_me()["name"] == "admin"
    assert res.test.post_login({"name": "kk"})
    assert res.test.get_me()["name"] == "kk"
