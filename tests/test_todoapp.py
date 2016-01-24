#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function
from todoapp import app


def test_base():
    with app.test_client() as c:
        assert 403 == c.get("/todo").status_code
        assert 403 == c.post("/todo").status_code
        assert 403 == c.put("/todo").status_code
        assert 403 == c.delete("/todo").status_code
        assert 403 == c.get("/todo/list").status_code

        assert 403 == c.get("/user").status_code
        assert 403 == c.post("/user").status_code
        assert 403 == c.put("/user").status_code
        assert 403 == c.delete("/user").status_code
        assert 403 == c.get("/user/list").status_code
        assert 400 == c.post("/user/register").status_code
        assert 400 == c.post("/user/login").status_code
        assert 403 == c.post("/user/logout").status_code
        assert True


def test_login():
    with app.test_client() as c:
        data = {"username": "guyskk", "password": "123456"}
        resp = c.post("/user/login", data=data)
        assert resp.status_code // 100 == 2
        assert b"id" in resp.data
        assert b"username" in resp.data
        assert "Authorization" in resp.headers


def login():
    with app.test_client() as c:
        data = {"username": "guyskk", "password": "123456"}
        resp = c.post("/user/login", data=data)
        return resp.headers["Authorization"]


def test_todo():
    import json
    with app.test_client() as c:
        headers = {
            "Authorization": login(),
            "Content-Type": "application/json"
        }
        data = json.dumps({"name": "todo_name"})
        assert 200 == c.post("/todo", data=data, headers=headers).status_code
        assert 200 == c.get("/todo?id=1", headers=headers).status_code
        data = json.dumps({"name": "todo_name", "id": 1})
        assert 200 == c.put("/todo", data=data, headers=headers).status_code
        assert 200 == c.get("/todo/list", headers=headers).status_code
        assert 200 == c.delete("/todo?id=1", headers=headers).status_code
