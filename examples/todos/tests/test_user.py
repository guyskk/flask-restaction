# coding:utf-8
from __future__ import unicode_literals
from todos import api


def test_get(res):
    with api.test_client() as c:
        assert c.user.get().code == 403
    resp = res.user.get()
    assert resp.code == 200
    assert resp.rv["name"] == "tester"
    assert resp.rv["photo"] == "http://pic.todos.com/photo/tester.png"
    assert "pwdhash" not in resp.rv


def test_put(res):
    resp = res.user.put({
        "name": "super_tester"
    })
    assert resp.code == 200
    assert resp.rv["message"] == "OK"
    resp = res.user.get()
    assert resp.code == 200
    assert resp.rv["name"] == "super_tester"
    assert resp.rv["photo"] == "http://pic.todos.com/photo/tester.png"
    assert "pwdhash" not in resp.rv
