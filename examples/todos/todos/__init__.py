# coding:utf-8
"""
管理员登录: res.user.post_login({email:"admin@todos.com",password:"123456"})
"""
from __future__ import unicode_literals
from flask import Flask, Blueprint, current_app
import os
from .extensions import api, db, auth
from .todos import Todos
from .user import User
from . import model
from flask_restaction import ApiInfo, Permission, Gen


def fn_user_role(token):
    if token and "id" in token:
        user = model.User.query.get(token["id"])
        if user:
            if user.email == current_app.config["ADMIN_EMAIL"]:
                return "admin"
            else:
                return "normal"
    return None


def before_first_request():
    db.create_all()
    email = current_app.config["ADMIN_EMAIL"]
    password = current_app.config["ADMIN_PASSWORD"]
    try:
        user = User().post(email, password)
        current_app.logger.info(user)
    except Exception as ex:
        current_app.logger.info(ex)


url_views = [
    ("/", "index.html"),
    ("/login", "login.html"),
    ("/signup", "signup.html"),
    ("/permission", "permission.html"),
]


def create_app():
    app = Flask(__name__)
    app.config["ADMIN_EMAIL"] = "admin@todos.com"
    app.config["ADMIN_PASSWORD"] = "123456"

    db_path = os.path.join(app.root_path, "todos.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
    app.config["SQLALCHEMY_ECHO"] = True
    db.init_app(app)

    bp_api = Blueprint('api', __name__, static_folder='static')
    api.init_app(app, blueprint=bp_api, docs=__doc__)
    auth.init_api(api, fn_user_role=fn_user_role)

    api.add_resource(Todos)
    api.add_resource(User)
    api.add_resource(Permission, auth=auth)
    api.add_resource(ApiInfo, api=api)

    def make_view(filename):
        return lambda *args, **kwargs: app.send_static_file(filename)
    for url, filename in url_views:
        end = os.path.splitext(filename)[0]
        app.route(url, endpoint=end)(make_view(filename))

    app.before_first_request(before_first_request)
    app.register_blueprint(bp_api, url_prefix='/api')

    gen = Gen(api)
    gen.resjs('static/js/res.js')
    gen.resdocs('static/resdocs.html', resjs='/static/js/res.js',
                bootstrap='/static/css/bootstrap.min.css')
    gen.permission('static/permission.html', resjs='/static/js/res.js',
                   bootstrap='/static/css/bootstrap.min.css',
                   vuejs='/static/js/vue.js')
    return app
