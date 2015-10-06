# coding:utf-8

from flask import request
from flask_restaction import Resource
from flask_restaction import abort, abort_if_not_me
from validater import add_validater
from validater.validaters import re_validater
from . import api
import re

user_roles = ["admin", "user", ]
users = {
    1: {
        "username": "guyskk",
        "password": "123456",
    }
}


re_password = re.compile(ur"""^[a-zA-Z0-9~!@#$%^&*(),./;'<>?:"-_=+]{6,20}$""")
add_validater("password", re_validater(re_password))


class User(Resource):
    schema_id = ("id", {
        "required": True, "validate": "int"
    })
    schema_username = ("username", {
        "desc": u"4-16个字符, 不能有特殊字符",
        "required": True, "validate": "re_name"
    })
    schema_password = ("password", {
        "desc": u"6-20个字符",
        "required": True, "validate": "password"
    })
    schema_inputs = {
        "get": dict([schema_id]),
        "get_list": dict(),
        "post": dict([schema_username, schema_password]),
        "put": dict([schema_id, schema_username, schema_password]),
        "delete": dict([schema_id]),
        "post_register": dict([schema_username, schema_password]),
        "put_setting": dict([schema_id, schema_username, schema_password]),
        "post_login": dict([schema_username, schema_password]),
        "post_logout": dict(),
    }

    schema_userinfo = dict([schema_id, schema_username])
    schema_outputs = {
        "get": schema_userinfo,
        "get_list": [schema_userinfo],
        "post": schema_userinfo,
        "put": schema_userinfo,
        "delete": dict(),
        "post_register": schema_userinfo,
        "put_setting": schema_userinfo,
        "post_login": schema_userinfo,
        "post_logout": dict(),
    }

    @staticmethod
    def user_role(uid):
        if uid == 1:
            return "admin"
        else:
            return "*"

    @staticmethod
    def abort_if_not_admin_or_me(id):
        if request.me["role"] != "admin":
            abort_if_not_me(id)

    def get(self, id):
        self.abort_if_not_admin_or_me(id)
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

    def put(self, id, **user):
        self.abort_if_not_admin_or_me(id)
        if id in users:
            users[id].update(user)
            return dict(users[id], id=id)
        else:
            abort(404)

    def delete(self, id):
        self.abort_if_not_admin_or_me(id)
        if id in users:
            del users[id]

    def post_register(self, **name_pass):
        return self.post(role="user", **name_pass)

    def put_setting(self, id, **name_pass):
        self.abort_if_not_admin_or_me(id)
        if id in users:
            users[id].update(name_pass)
            return dict(users[id], id=id)
        else:
            abort(404)

    def post_login(self, username, password):
        for k, u in users.items():
            if u.get("username") == username and u.get("password") == password:
                me = {"id": k}
                return dict(u, id=k), api.gen_auth_header(me)
        abort(403, u"登录失败")

    def post_logout(self):
        auth = {api.auth_header: api.gen_token(request.me, auth_exp=-1)}
        return {}, auth
