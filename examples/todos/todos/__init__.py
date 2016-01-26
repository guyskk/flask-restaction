# coding:utf-8
from __future__ import unicode_literals
"""
admin login: res.user.post_login({email:"admin@todos.com",password:"123456"})
"""
from flask import Flask, Blueprint, current_app
import os
from .extensions import api, db
from .todos import Todos
from .user import User
from . import model


def fn_user_role(userid):
    user = model.User.query.get(userid)
    if user and user.email == current_app.config["ADMIN_EMAIL"]:
        return "admin"
    else:
        return "normal"


def before_first_request():
    db.create_all()
    api.gen_resjs()
    api.gen_resdocs()
    email = current_app.config["ADMIN_EMAIL"]
    password = current_app.config["ADMIN_PASSWORD"]
    try:
        user = User().post(email, password)
        current_app.logger.info(user)
    except Exception as ex:
        current_app.logger.info(ex)


url_views = [
    ("/", "index.html"),
    ("/permission", "permission.html"),
    ("/login", "login.html"),
    ("/signup", "signup.html")
]


def create_app():
    app = Flask(__name__)
    app.config["API_BOOTSTRAP"] = "/static/css/bootstrap.min.css"
    app.config["API_RESJS_NAME"] = "js/res.js"
    app.config["ADMIN_EMAIL"] = "admin@todos.com"
    app.config["ADMIN_PASSWORD"] = "123456"

    db_path = os.path.join(app.root_path, "todos.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
    app.config["SQLALCHEMY_ECHO"] = True
    db.init_app(app)

    bp_api = Blueprint('api', __name__, static_folder='static')
    api.init_app(bp_api, fn_user_role=fn_user_role, docs=__doc__)
    api.config(app.config)

    api.add_resource(Todos)
    api.add_resource(User)
    api.add_permission_resource()

    def make_view(filename):
        return lambda *args, **kwargs: app.send_static_file(filename)
    for url, filename in url_views:
        end = os.path.splitext(filename)[0]
        app.route(url, endpoint=end)(make_view(filename))

    app.before_first_request(before_first_request)
    app.register_blueprint(bp_api, url_prefix='/api')
    return app
