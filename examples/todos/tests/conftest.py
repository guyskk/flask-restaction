# coding:utf-8
from __future__ import unicode_literals
from todos import api, create_app
import pytest
app = create_app()


@pytest.yield_fixture()
def newuser():
    with api.test_client("tester@todos.com") as c:
        resp = c.user.delete()
        assert resp.code == 200 or resp.code == 403
    with api.test_client() as c:
        resp = c.user.post({
            "email": "tester@todos.com",
            "password": "123456"
        })
        assert resp.code == 200
        yield resp.rv
    with api.test_client("tester@todos.com") as c:
        resp = c.user.delete()
        assert resp.code == 200


@pytest.yield_fixture
def res(newuser):
    with api.test_client("tester@todos.com") as c:
        yield c
