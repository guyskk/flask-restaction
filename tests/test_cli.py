import requests
from unittest import mock
from flask_restaction.cli import parse_meta, resjs, main


def test_url_prefix():
    url = "http://127.0.0.1:5000"
    meta = requests.get(url, headers={'Accept': 'application/json'}).json()
    url_prefix, __, __ = parse_meta(meta)
    assert url_prefix == ""


def test_resjs_web(tmpdir):
    resjs("http://127.0.0.1:5000", tmpdir.join("res.js").strpath,
          prefix="/api", min=True)
    assert tmpdir.join("res.js").check()


def test_resjs_node(tmpdir):
    resjs("http://127.0.0.1:5000", tmpdir.join("res.js").strpath, node=True)
    assert tmpdir.join("res.js").check()


def test_api_meta_view():
    resjs = requests.get("http://127.0.0.1:5000?f=res.js")
    assert resjs.headers["Content-Type"] == "application/javascript"
    resminjs = requests.get("http://127.0.0.1:5000?f=res.min.js")
    assert resminjs.headers["Content-Type"] == "application/javascript"
    resjs2 = requests.get("http://127.0.0.1:5000?f=res.js")
    assert resjs.content == resjs2.content
    resminjs2 = requests.get("http://127.0.0.1:5000?f=res.min.js")
    assert resminjs.content == resminjs2.content
    resp = requests.get("http://127.0.0.1:5000?f=docs.min.js")
    assert resp.status_code == 200
    resp = requests.get("http://127.0.0.1:5000?f=docs.min.css")
    assert resp.status_code == 200
    resp = requests.get("http://127.0.0.1:5000?f=unknown.js")
    assert resp.status_code == 404


def test_cli(tmpdir):
    dest = tmpdir.join("res.js").strpath
    args = ["resjs", "http://127.0.0.1:5000", "-d", dest]
    with mock.patch("sys.argv", new=args):
        main()
