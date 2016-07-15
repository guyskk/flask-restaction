from flask_restaction.cli import resjs


def test_cli(tmpdir):
    resjs("http://127.0.0.1:5000", tmpdir.strpath)
    assert tmpdir.join("res.js").check()
    assert tmpdir.join("res.min.js").check()
