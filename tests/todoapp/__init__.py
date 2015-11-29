# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import
from flask import Flask
from flask_restaction import Api
from datetime import datetime
from validater import add_validater


def user_role(uid):
    if uid == 1:
        return "admin"


def iso_datetime_validater(v):
    if isinstance(v, datetime):
        return (True, v.isoformat())
    else:
        return (False, None)
add_validater("iso_datetime", iso_datetime_validater)

app = Flask(__name__)
app.debug = True
api = Api(app, fn_user_role=user_role)
app.config["JSON_AS_ASCII"] = False

from .users import User
from .todos import Todo
api.add_resource(User)
api.add_resource(Todo)
api.gen_resjs()
api.gen_resdocs()
