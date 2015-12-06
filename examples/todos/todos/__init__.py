# coding:utf-8
from __future__ import unicode_literals
"""
管理员登录
    res.user.post_login({email:"admin@todos.com",password:"123456"})
"""
from flask import Flask, Blueprint, g, current_app
import os
from sqlitedict import SqliteDict
from werkzeug.security import generate_password_hash
from .extensions import api
from .todos import Todos
from .user import User


def connect_db():
    if not hasattr(g, "db"):
        sqlite = current_app.config["SQLITE"]
        g.db = SqliteDict(sqlite)


def close_db(*resp):
    if hasattr(g, "db"):
        g.db.close()
        del g.db
    return resp


def fn_user_role(email):
    u = g.db.get(email)
    if u:
        if email == current_app.config["ADMIN_EMAIL"]:
            return "admin"
        else:
            return "normal"


def before_first_request():
    api.gen_resjs()
    api.gen_resdocs()
    email = current_app.config["ADMIN_EMAIL"]
    sqlite = current_app.config["SQLITE"]
    with SqliteDict(sqlite) as db:
        pwdhash = generate_password_hash(current_app.config["ADMIN_PASSWORD"])
        db[email] = {
            "nickname": "admin",
            "pwdhash": pwdhash
        }
        db.commit()

url_views = [
    ("/", "index.html"),
    ("/permission", "permission.html"),
    ("/login", "login.html"),
    ("/signup", "signup.html")
]


def create_app():
    app = Flask(__name__)
    app.config["SQLITE"] = "todos.db"
    app.config["API_BOOTSTRAP"] = "/static/bootstrap.min.css"
    app.config["API_BOOTSTRAP"] = "/static/bootstrap.min.css"
    app.config["ADMIN_EMAIL"] = "admin@todos.com"
    app.config["ADMIN_PASSWORD"] = "123456"

    bp_api = Blueprint('api', __name__, static_folder='static')
    api.init_app(bp_api, fn_user_role=fn_user_role, docs=__doc__)
    api.config(app.config)

    api.add_resource(Todos)
    api.add_resource(User)
    api.add_permission_resource()

    api.before_request(connect_db)
    api.after_request(close_db)

    def make_view(filename):
        return lambda *args, **kwargs: app.send_static_file(filename)
    for url, filename in url_views:
        end = os.path.splitext(filename)[0]
        app.route(url, endpoint=end)(make_view(filename))

    app.before_first_request(before_first_request)
    app.register_blueprint(bp_api, url_prefix='/api')
    return app
