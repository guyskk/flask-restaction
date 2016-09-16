from flask_restaction.cli import parse_meta, resjs


def test_url_prefix():
    url_prefix, __, __ = parse_meta("http://127.0.0.1:5000/")
    # strip end '/'
    assert url_prefix == "http://127.0.0.1:5000"


def test_resjs_web(tmpdir):
    resjs("http://127.0.0.1:5000", tmpdir.join("res.js").strpath,
          prefix="/api", min=True)
    assert tmpdir.join("res.js").check()


def test_resjs_node(tmpdir):
    resjs("http://127.0.0.1:5000", tmpdir.join("res.js").strpath, node=True)
    assert tmpdir.join("res.js").check()
