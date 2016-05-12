# coding:utf-8
from __future__ import unicode_literals


def test_get(guest, res):
    assert guest.user.get().status_code == 403
    resp = res.user.get()
    assert resp.status_code == 200
    assert resp.json["email"] == "tester@todos.com"
    assert resp.json["photo"] == ""
    assert "pwdhash" not in resp.json


def test_put(res):
    resp = res.user.put({
        "name": "super_tester"
    })
    assert resp.status_code == 200
    assert resp.json["name"] == "super_tester"
    resp = res.user.get()
    assert resp.status_code == 200
    assert resp.json["name"] == "super_tester"
    assert resp.json["photo"] == ""
    assert "pwdhash" not in resp.json
