# coding:utf-8
from __future__ import unicode_literals
from flask import request, abort
from flask_restaction import Resource
from . import api

users = {
    1: {
        "username": "guyskk",
        "password": "123456",
    }
}


class User(Resource):
    userid = "int&required"
    username = "name&required", "4-16个字符, 不能有特殊字符"
    password = "password&required", "6-20个字符"
    schema_inputs = {
        "get": {"id": userid},
        "get_list": None,
        "post": {"username": username, "password": password},
        "put": {"id": userid, "username": username, "password": password},
        "delete": {"id": userid},
        "post_register": {"username": username, "password": password},
        "post_login": {"username": username, "password": password},
        "post_logout": None,
    }

    userinfo = {"id": userid, "username": username}
    schema_outputs = {
        "get": userinfo,
        "get_list": [userinfo],
        "post": userinfo,
        "put": userinfo,
        "delete": None,
        "post_register": userinfo,
        "post_login": userinfo,
        "post_logout": None,
    }

    def get(self):
        id = request.me["id"]
        if id in users:
            return dict(users[id], id=id)
        else:
            abort(404)

    def get_list(self):
        return [dict(u, id=i) for i, u in users.items()]

    def post(self, **user):
        if users:
            newid = max(users) + 1
        else:
            newid = 1
        users[newid] = user
        return dict(user, id=newid)

    def put(self, **user):
        id = request.me["id"]
        if id in users:
            users[id].update(user)
            return dict(users[id], id=id)
        else:
            abort(404)

    def delete(self):
        id = request.me["id"]
        if id in users:
            del users[id]

    def post_register(self, **name_pass):
        return self.post(role="user.user", **name_pass)

    def post_login(self, username, password):
        for k, u in users.items():
            if u.get("username") == username and u.get("password") == password:
                me = {"id": k}
                return dict(u, id=k), api.gen_auth_header(me)
        abort(403, "登录失败")

    def post_logout(self):
        auth = {api.auth_header: api.gen_token(request.me, auth_exp=-1)}
        return {}, auth
