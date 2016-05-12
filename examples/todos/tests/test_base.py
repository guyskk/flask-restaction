# coding:utf-8
from __future__ import unicode_literals


def test_base(app):
    with app.test_client() as c:
        assert c.get("/").status_code == 200
