# coding:utf-8

from __future__ import unicode_literals
from flask_restaction import Resource
from flask import abort
from datetime import datetime


todos = {}


class Todo(Resource):

    """docstring for Todo"""

    todoid = "int&required", "todo's id"
    name = "name&required", "名称"
    date_out = "datetime&required&output", "时间"
    date_in = {
        "validater": "datetime",
        "required": True,
        "default": datetime.now,
        "desc": "时间"
    }
    finish = "bool&required&default=False", "是否已完成"
    schema_inputs = {
        "get": {"id": todoid},
        "post": {"name": name, "date": date_in, "finish": finish},
        "put": {"id": todoid, "name": name, "date": date_in, "finish": finish},
        "delete": {"id": todoid}
    }
    info = {"name": name, "date": date_out, "finish": finish}
    schema_outputs = {
        "get": info,
        "get_list": [info],
        "post": info,
        "put": info,
    }
    output_types = []

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
