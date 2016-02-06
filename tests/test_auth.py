#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function

from flask_restaction.auth import permit, parse_config
from flask import Flask, g
from flask_restaction import Api, Resource, Auth, Permission, Res
import pytest


@pytest.fixture
def app():
    app = Flask(__name__)
    app.debug = True
    app.config["API_RESOURCE_JSON"] = "testdata/resource.json"
    app.config["API_PERMISSION_JSON"] = "testdata/permission.json"

    def fn_user_role(token):
        user_id = token["id"]
        user_roles = ["访客", "普通用户", "管理员"]
        return user_roles[user_id]

    api = Api(app)
    auth = Auth(api, fn_user_role=fn_user_role)

    class User(Resource):

        schema_inputs = {"post": {"id": "int(0,2)&required"}}

        def get(self):
            return "ok"

        def post(self, id):
            return "ok", auth.gen_header({"id": id})

    api.add_resource(User)
    api.add_resource(Permission, auth=auth)
    app.api = api
    app.auth = auth
    return app


def test_permit():
    resource = {
        "photo": {
            "other": ["get"]
        },
        "article": {
            "other": ["get"],
            "writer": ["post", "put"]
        },
        "apiinfo": {}
    }
    permission = {
        "roleA": {
            "photo": "other",
            "article": "writer"
        },
        "roleB": {
            "photo": "other",
            "article": "owner"
        },
        "roleC": {
            "photo": "owner",
            "article": "other"
        }
    }

    config = parse_config(resource, permission)

    assert permit(config, "roleA", "photo", "get")[0]
    assert permit(config, "roleB", "photo", "get")[0]
    assert permit(config, "roleC", "photo", "get")[0]

    assert not permit(config, "roleA", "photo", "post")[0]
    assert not permit(config, "roleB", "photo", "post")[0]
    assert permit(config, "roleC", "photo", "post")[0]

    assert permit(config, "roleA", "article", "get")[0]
    assert permit(config, "roleB", "article", "get")[0]
    assert permit(config, "roleC", "article", "get")[0]

    assert permit(config, "roleA", "article", "post")[0]
    assert permit(config, "roleB", "article", "post")[0]
    assert not permit(config, "roleC", "article", "post")[0]

    assert not permit(config, "roleA", "article", "delete")[0]
    assert permit(config, "roleB", "article", "delete")[0]
    assert not permit(config, "roleC", "article", "delete")[0]

    assert permit(config, "root", "photo", "get")[0]
    assert permit(config, "root", "photo", "post")[0]
    assert permit(config, "root", "photo", "delete")[0]
    assert permit(config, "root", "article", "get")[0]
    assert permit(config, "root", "article", "post")[0]
    assert permit(config, "root", "article", "delete")[0]
    assert permit(config, "root", "unknown", "get")[0]
    assert permit(config, "root", "unknown", "post")[0]
    assert permit(config, "root", "unknown", "delete")[0]


def test_parse_config_error():

    # resource name must be lowcase
    resource = {"HELLO": {"other": ["get"]}}
    permission = {"role": {"hello": "owner"}}
    with pytest.raises(AssertionError):
        parse_config(resource, permission)

    # invalid action
    resource = {"hello": {"other": ["unknown"]}}
    permission = {"role": {"hello": "owner"}}
    with pytest.raises(AssertionError):
        parse_config(resource, permission)

    # root can't be modified
    resource = {"hello": {"other": ["get"]}}
    permission = {"root": {"hello": "owner"}}
    with pytest.raises(AssertionError):
        parse_config(resource, permission)

    # resource not exists
    resource = {"hello": {"other": ["get"]}}
    permission = {"role": {"unknown": "get"}}
    with pytest.raises(AssertionError):
        parse_config(resource, permission)

    # res_role not exists
    resource = {"hello": {"other": ["get"]}}
    permission = {"role": {"hello": "unknown"}}
    with pytest.raises(AssertionError):
        parse_config(resource, permission)


def test_user(app):

    with app.test_client() as c:
        assert c.get("/user").status_code == 403
        resp = c.post("/user", data={"id": 0})
        assert resp.status_code == 200
        assert resp.data == b"ok"
        # user_role=访客
        assert c.get("/user", headers=resp.headers).status_code == 403
        assert g.user_role == "访客"
        assert g.token['id'] == 0
        assert g.res_role == "other"
        assert c.get("/permission",
                     headers=resp.headers).status_code == 403

    with app.test_client() as c:
        assert c.get("/user").status_code == 403
        resp = c.post("/user", data={"id": 1})
        assert resp.status_code == 200
        assert resp.data == b"ok"
        # user_role=普通用户
        assert c.get("/user", headers=resp.headers).status_code == 200
        assert c.get("/user", headers=resp.headers).data == b"ok"
        assert c.get("/permission", headers=resp.headers).status_code == 200

    with app.test_client() as c:
        assert c.get("/user").status_code == 403
        resp = c.post("/user", data={"id": 2})
        assert resp.status_code == 200
        assert resp.data == b"ok"
        # user_role=管理员
        assert c.get("/permission/permit",
                     headers=resp.headers).status_code == 400
        assert c.get("/permission",
                     headers=resp.headers).status_code == 200
        assert c.post("/permission",
                      headers=resp.headers).status_code == 400
        assert c.delete("/permission",
                        headers=resp.headers).status_code == 400


def test_permission(app):
    res = Res(app.api)
    rv, code, headers = res.user.post({"id": 2})
    assert code == 200
    res = Res(app.api, headers=headers)
    p = res.permission
    assert p.get_permit({"user_role": "普通用户",
                         "resource": "user",
                         "action": "get"}).rv['permit']
    assert not p.get_permit({"user_role": "普通用户",
                             "resource": "permission",
                             "action": "post"}).rv['permit']
    data = {
        "user_role": "RoleX",
        "resource": {
            "user": "normal",
            "permission": "owner"
        }
    }
    assert p.post(data).code == 200
    assert p.get_permit({"user_role": "RoleX", "resource": "user",
                         "action": "get"}).rv['permit']
    assert p.get_permit({"user_role": "RoleX", "resource": "permission",
                         "action": "post"}).rv['permit']
    assert p.delete({"user_role": "RoleX"}).code == 200
    assert not p.get_permit({"user_role": "RoleX", "resource": "user",
                             "action": "get"}).rv['permit']
    assert not p.get_permit({"user_role": "RoleX", "resource": "permission",
                             "action": "post"}).rv['permit']
