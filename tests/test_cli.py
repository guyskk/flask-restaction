from flask_restaction.cli import parse_meta, resjs


def test_url_prefix():
    url_prefix, __, __ = parse_meta("http://127.0.0.1:5000/")
    # strip end '/'
    assert url_prefix == "http://127.0.0.1:5000"


def test_cli(tmpdir):
    resjs("http://127.0.0.1:5000", tmpdir.join("res.js").strpath)
    assert tmpdir.join("res.js").check()
