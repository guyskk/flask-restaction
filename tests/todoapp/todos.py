# coding:utf-8

from __future__ import unicode_literals
from flask_restaction import Resource
from flask import abort
from datetime import datetime


todos = {}


class Todo(Resource):

    """docstring for Todo"""

    schema_id = ("id", {
        "desc": "todo's id",
        "required": True,
        "validate": "int",
    })
    schema_name = ("name", {
        "desc": "名称",
        "required": True,
        "validate": "name",
    })
    schema_date_out = ("date", {
        "desc": "时间",
        "required": True,
        "validate": "iso_datetime",
    })
    schema_date_in = ("date", {
        "desc": "时间",
        "required": True,
        "validate": "datetime",
        "default": datetime.now
    })
    schema_finish = ("finish", {
        "desc": "是否已完成",
        "required": True,
        "validate": "bool",
        "default": False
    })
    schema_inputs = {
        "get": dict([schema_id]),
        "post": dict([schema_name, schema_date_in, schema_finish]),
        "put": dict([schema_id, schema_name, schema_date_in, schema_finish]),
        "delete": dict([schema_id]),
    }
    schema_out = dict([schema_id, schema_name, schema_date_out, schema_finish])
    schema_outputs = {
        "get": schema_out,
        "get_list": [schema_out],
        "post": schema_out,
        "put": schema_out,
    }
    types = []

    @staticmethod
    def user_role(uid):
        if uid == 1:
            return "admin"
        else:
            return "*"

    def get(self, id):
        if id in todos:
            return dict(todos[id], id=id)
        else:
            abort(404)

    def get_list(self):
        return [dict(v, id=k) for k, v in todos.items()]

    def post(self, **todo):
        if not todos:
            newid = 1
        else:
            newid = max(todos) + 1
        todos[newid] = todo
        return dict(todo, id=newid)

    def put(self, id, **todo):
        if id in todos:
            todos[id] = todo
            return dict(todo, id=id)
        else:
            abort(404)

    def delete(self, id):
        if id in todos:
            del todos[id]
