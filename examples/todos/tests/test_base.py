# coding:utf-8
from __future__ import unicode_literals
from todos import create_app
app = create_app()


def test_base():
    with app.test_client() as c:
        assert c.get("/").status_code == 200
