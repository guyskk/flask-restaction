# coding:utf-8
from __future__ import unicode_literals
from flask import g, abort
from flask.ext.restaction import Resource, schema
from werkzeug.security import generate_password_hash, check_password_hash
from . import api


class User(Resource):
    """User"""
    email = "email&required"
    password = "password&required"
    new_password = "password&required"
    nickname = "unicode"
    photo = "url"
    message = "unicode"

    info = schema("nickname", "photo")
    schema_inputs = {
        "get": None,
        "post": schema("email", "password", "nickname", "photo"),
        "post_login": schema("email", "password"),
        "put_password": schema("email", "password", "new_password"),
        "put": schema("nickname", "photo"),
        "delete": None
    }
    schema_outputs = {
        "get": info,
        "post": info,
        "post_login": info,
        "put_password": schema("message"),
        "put": schema("message"),
        "delete": schema("message")
    }

    def get(self):
        """获取个人信息"""
        email = g.me["id"]
        return g.db[email]

    def post(self, email, password, **info):
        """注册"""
        if email in g.db:
            abort(400, "user email=%s already exists" % email)
        pwdhash = generate_password_hash(password)
        info["pwdhash"] = pwdhash
        g.db[email] = info
        g.db.commit()
        return info

    def post_login(self, email, password):
        """登录"""
        if email not in g.db:
            abort(404, "user email=%s not exists" % email)
        info = g.db[email]
        if not check_password_hash(info["pwdhash"], password):
            abort(403, "Incorrect email or password")
        header = api.gen_auth_header({"id": email})
        return info, header

    def put_password(self, password, new_password):
        """修改密码"""
        email = g.me["id"]
        info, __ = self.post_login(email, password)
        info["pwdhash"] = generate_password_hash(new_password)
        g.db[email] = info
        g.db.commit()
        return {"message": "OK"}

    def put(self, **info):
        """修改个人信息"""
        info = {k: v for k, v in info.items() if v != ""}
        email = g.me["id"]
        g.db[email] = dict(g.db[email], **info)
        g.db.commit()
        return {"message": "OK"}

    def delete(self):
        """删除账号"""
        email = g.me["id"]
        if email in g.db:
            del g.db[email]
            g.db.commit()
        return {"message": "OK"}
