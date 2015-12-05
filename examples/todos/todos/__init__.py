# coding:utf-8
from __future__ import unicode_literals
"""
注册
    res.user.post({email:"admin@todos.com",password:"123456"})
登录
    res.user.post_login({email:"admin@todos.com",password:"123456"})
"""
from flask import Flask, g, current_app
from flask.ext.restaction import Api
from sqlitedict import SqliteDict

api = Api()

from .todos import Todos
from .user import User


def connect_db():
    if not hasattr(g, "db"):
        sqlite = current_app.config["SQLITE"]
        g.db = SqliteDict(sqlite)


def close_db(*resp):
    if hasattr(g, "db"):
        g.db.close()
    return resp


def before_first_request():
    api.gen_resjs()
    api.gen_resdocs()


def fn_user_role(email):
    u = g.db.get(email)
    if u:
        return "normal"


def create_app():
    app = Flask(__name__)
    app.config["SQLITE"] = "todos.db"
    api.init_app(app, fn_user_role=fn_user_role, docs=__doc__)
    api.before_request(connect_db)
    api.after_request(close_db)
    api.add_resource(Todos)
    api.add_resource(User)
    api.add_permission_resource()
    app.before_first_request(before_first_request)
    return app
